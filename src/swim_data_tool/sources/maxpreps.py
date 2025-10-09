"""MaxPreps data source plugin for high school swimming.

This plugin scrapes MaxPreps website for high school swimming data.
"""

import json
import os
import re
import time
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup

from swim_data_tool.sources.base import SwimDataSource


class MaxPrepsSource(SwimDataSource):
    """MaxPreps high school swimming data source.

    Scrapes roster and athlete data from MaxPreps website.
    Requires Playwright for headless browser automation.
    """

    @property
    def source_name(self) -> str:
        """Human-readable source name."""
        return "MaxPreps"

    @property
    def swimmer_id_field(self) -> str:
        """Field name for unique swimmer ID."""
        return "careerid"

    def __init__(self):
        """Initialize MaxPreps source."""
        self.base_url = "https://www.maxpreps.com"
        self.school_slug = os.getenv("MAXPREPS_SCHOOL_SLUG", "")
        self.state = os.getenv("MAXPREPS_STATE", "").lower()
        self.city = os.getenv("MAXPREPS_CITY", "").lower()
        self.seasons = os.getenv("MAXPREPS_SEASONS", "24-25").split(",")

        # Initialize Playwright
        self._playwright = None
        self._browser = None

    def _ensure_playwright(self):
        """Ensure Playwright is initialized."""
        if self._playwright is None:
            try:
                from playwright.sync_api import sync_playwright

                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(headless=True)
            except ImportError:
                raise ImportError(
                    "Playwright is required for MaxPreps source. "
                    "Install with: pip install playwright && playwright install chromium"
                )

    def _fetch_page(self, url: str, wait_time: int = 3000) -> str:
        """Fetch page content using Playwright.

        Args:
            url: URL to fetch
            wait_time: Time to wait after page load (milliseconds)

        Returns:
            HTML content
        """
        self._ensure_playwright()

        page = self._browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(wait_time)
            html = page.content()
            return html
        finally:
            page.close()
            # Be polite to the server
            time.sleep(1)

    def get_team_roster(self, team_id: str, seasons: list[str] | None = None) -> pd.DataFrame:
        """Fetch team roster from MaxPreps.

        Args:
            team_id: School slug (e.g., "tanque-verde-hawks")
            seasons: List of seasons (e.g., ["24-25", "23-24"])

        Returns:
            DataFrame with columns:
                - careerid: Unique athlete ID
                - swimmer_name: Full name
                - gender: "M" or "F"
                - grade: Grade abbreviation (Fr., So., Jr., Sr.)
                - grade_numeric: Numeric grade (9, 10, 11, 12)
                - school_name: School name
                - season: Season year
        """
        if not team_id:
            team_id = self.school_slug

        if seasons is None:
            seasons = self.seasons

        all_rosters = []

        for season in seasons:
            # Scrape boys roster
            boys_df = self._scrape_roster(team_id, season, "boys")
            if not boys_df.empty:
                boys_df["gender"] = "M"
                all_rosters.append(boys_df)

            # Scrape girls roster
            girls_df = self._scrape_roster(team_id, season, "girls")
            if not girls_df.empty:
                girls_df["gender"] = "F"
                all_rosters.append(girls_df)

        if not all_rosters:
            return pd.DataFrame()

        # Combine and deduplicate
        combined = pd.concat(all_rosters, ignore_index=True)

        # Deduplicate by careerid, keeping most recent season
        deduplicated = combined.sort_values("season", ascending=False)
        deduplicated = deduplicated.drop_duplicates(subset=["careerid"], keep="first")

        return deduplicated

    def _scrape_roster(self, school_slug: str, season: str, gender_path: str) -> pd.DataFrame:
        """Scrape roster for one gender/season.

        Args:
            school_slug: School identifier
            season: Season (e.g., "24-25")
            gender_path: "boys" or "girls"

        Returns:
            DataFrame with roster data
        """
        # Build URL
        if gender_path == "boys":
            url = f"{self.base_url}/{self.state}/{self.city}/{school_slug}/swimming/fall/{season}/roster/"
        else:
            url = f"{self.base_url}/{self.state}/{self.city}/{school_slug}/swimming/{gender_path}/fall/{season}/roster/"

        print(f"  Fetching {gender_path} roster: {season}")

        try:
            html = self._fetch_page(url)
        except Exception as e:
            print(f"    ⚠️  Failed to fetch {gender_path} roster for {season}: {e}")
            return pd.DataFrame()

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")

        # Find roster table
        roster_table = soup.find("table")
        if not roster_table:
            print(f"    No roster table found for {gender_path}")
            return pd.DataFrame()

        # Extract athletes
        athletes = []
        for row in roster_table.find_all("tr")[1:]:  # Skip header
            cols = row.find_all("td")
            if len(cols) < 3:  # Need at least 3 columns (empty, name, grade)
                continue

            # Second column (index 1) has athlete link
            link = cols[1].find("a")
            if not link:
                continue

            name = link.get_text(strip=True)
            href = link.get("href", "")

            # Extract careerid from URL
            careerid_match = re.search(r"careerid=([a-z0-9]+)", href)
            if not careerid_match:
                continue

            careerid = careerid_match.group(1)

            # Third column (index 2) has grade
            grade = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            grade_numeric = self._parse_grade(grade)

            athletes.append(
                {
                    "careerid": careerid,
                    "swimmer_name": name,
                    "grade": grade,
                    "grade_numeric": grade_numeric,
                    "school_name": school_slug.replace("-", " ").title(),
                    "season": season,
                    "athlete_url": f"{self.base_url}{href}",
                }
            )

        print(f"    Found {len(athletes)} athletes")

        return pd.DataFrame(athletes)

    def _parse_grade(self, grade_str: str) -> int | None:
        """Parse grade abbreviation to numeric grade.

        Args:
            grade_str: Grade string (e.g., "Fr.", "So.", "Jr.", "Sr.")

        Returns:
            Numeric grade (9-12) or None
        """
        grade_map = {
            "fr.": 9,
            "so.": 10,
            "jr.": 11,
            "sr.": 12,
            "freshman": 9,
            "sophomore": 10,
            "junior": 11,
            "senior": 12,
        }
        return grade_map.get(grade_str.lower())

    def get_swimmer_history(
        self,
        swimmer_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """Fetch swimmer history from MaxPreps.

        Args:
            swimmer_id: careerid or full athlete URL
            start_year: Not used for MaxPreps (gets all available data)
            end_year: Not used for MaxPreps (gets all available data)

        Returns:
            DataFrame with canonical columns
        """
        print(f"    Fetching athlete: {swimmer_id}")

        # First, fetch the athlete's main page to find the correct stats link
        if swimmer_id.startswith("http"):
            athlete_url = swimmer_id
        else:
            athlete_url = swimmer_id

        try:
            # Fetch main athlete page
            main_html = self._fetch_page(athlete_url)
            main_soup = BeautifulSoup(main_html, "html.parser")

            # Look for the swimming stats link on the page
            # Girls: /athletes/NAME/swimming/girls/stats/?careerid=XXX
            # Boys: /athletes/NAME/swimming/stats/?careerid=XXX
            stats_url = None
            for link in main_soup.find_all("a", href=True):
                href = link["href"]
                if "/swimming/girls/stats/" in href or "/swimming/stats/" in href:
                    if "?" in href:  # Has careerid
                        # Convert relative URL to absolute
                        if href.startswith("/"):
                            stats_url = f"{self.base_url}{href}"
                        else:
                            stats_url = href
                        break

            # If we didn't find a stats link, construct one manually
            if not stats_url:
                # Try both boys and girls paths
                if "?" in athlete_url:
                    base_url, query = athlete_url.split("?", 1)
                    base_url = base_url.rstrip("/")
                    # Try boys path first
                    stats_url = f"{base_url}/swimming/stats/?{query}"
                else:
                    stats_url = f"{athlete_url.rstrip('/')}/swimming/stats/"

        except Exception as e:
            print(f"      ⚠️  Failed to fetch athlete page: {e}")
            return pd.DataFrame()

        # Fetch the stats page
        try:
            html = self._fetch_page(stats_url)
        except Exception as e:
            print(f"      ⚠️  Failed to fetch stats page: {e}")
            return pd.DataFrame()

        # Parse stats page
        soup = BeautifulSoup(html, "html.parser")

        # Extract metadata from embedded JSON
        metadata = self._extract_athlete_metadata(html)

        # Extract swim times from HTML tables
        swims = self._extract_swim_times(soup, metadata)

        return swims

    def _extract_athlete_metadata(self, html: str) -> dict[str, Any]:
        """Extract athlete metadata from embedded JSON in HTML.

        Args:
            html: Page HTML

        Returns:
            Dictionary with metadata
        """
        soup = BeautifulSoup(html, "html.parser")

        # Search for script tag with athlete data
        for script in soup.find_all("script"):
            if not script.string:
                continue

            if "careerName" in script.string:
                # Try to extract JSON object
                match = re.search(r'\{[^<>]*"careerName"[^<>]*\}', script.string)
                if match:
                    try:
                        data = json.loads(match.group(0))
                        return data
                    except json.JSONDecodeError:
                        continue

        return {}

    def _extract_swim_times(self, soup: BeautifulSoup, metadata: dict[str, Any]) -> pd.DataFrame:
        """Extract swim times from HTML tables on MaxPreps stats page.

        MaxPreps organizes stats by season, with each season in a separate section.
        Each section has a grade indicator (Freshman/Sophomore/Junior/Senior).
        We extract the grade for each section and assign it to all swims in that section.

        Args:
            soup: BeautifulSoup object of the stats page
            metadata: Athlete metadata

        Returns:
            DataFrame with swim times
        """
        swimmer_name = metadata.get("careerName", "")
        gender = "M" if metadata.get("gender") == "Boys" else "F"
        school_name = metadata.get("schoolName", "")

        all_swims = []

        # Grade name to numeric mapping
        grade_map = {
            "freshman": 9,
            "sophomore": 10,
            "junior": 11,
            "senior": 12,
        }

        # Find all meet-stats sections (one per season)
        stat_sections = soup.find_all("div", class_="meet-stats")

        if not stat_sections:
            # Fallback: if no sections found, try processing all tables with current grade
            stat_sections = [soup]

        for section in stat_sections:
            # Extract grade for this section
            grade_numeric = None

            # Look for grade indicator in parent or nearby text
            parent = section.find_parent()
            if parent:
                parent_text = parent.get_text()
                for grade_name, grade_num in grade_map.items():
                    if grade_name.lower() in parent_text.lower():
                        grade_numeric = grade_num
                        break

            # If still no grade found, try to extract from metadata (current grade)
            if grade_numeric is None:
                content = metadata.get("content", "")
                grade_match = re.search(r"career-current-grade-(\d+)", content)
                if grade_match:
                    grade_numeric = int(grade_match.group(1))

            # Find all tables in this section
            tables = section.find_all("table", class_="mx-grid")

            for table in tables:
                # Get the preceding heading to find the event name
                # Look back for h2, h3, h4, etc.
                heading = table.find_previous(["h2", "h3", "h4", "h5"])
                if not heading:
                    continue

                event_name = heading.get_text(strip=True)

                # Skip "Best Finishes" summary tables
                if event_name == "Best Finishes":
                    continue

                # Check if this is a times table (has Date, Opponent, Round, Splits, Time headers)
                headers = [th.get_text(strip=True) for th in table.find_all("th")]
                if "Date" not in headers or "Time" not in headers:
                    continue

                # Parse each row
                tbody = table.find("tbody")
                if not tbody:
                    continue

                for row in tbody.find_all("tr"):
                    cols = row.find_all("td")
                    if len(cols) < 5:
                        continue

                    # Relay events have 6 columns (Name, Date, Opponent, Round, Splits, Time)
                    # Individual events have 5 columns (Date, Opponent, Round, Splits, Time)
                    is_relay = len(cols) >= 6

                    if is_relay:
                        # Skip the "Name" column (which says "Relay Team")
                        date = cols[1].get_text(strip=True)
                        meet_link = cols[2].find("a")
                        meet_name = meet_link.get_text(strip=True) if meet_link else cols[2].get_text(strip=True)
                        round_type = cols[3].get_text(strip=True)
                        splits = cols[4].get_text(strip=True)
                        time = cols[5].get_text(strip=True)
                    else:
                        date = cols[0].get_text(strip=True)
                        meet_link = cols[1].find("a")
                        meet_name = meet_link.get_text(strip=True) if meet_link else cols[1].get_text(strip=True)
                        round_type = cols[2].get_text(strip=True)
                        splits = cols[3].get_text(strip=True)
                        time = cols[4].get_text(strip=True)

                    if not time or time == "":
                        continue

                    # Normalize MaxPreps event names to USA Swimming format
                    # MaxPreps: "100 Breast" -> USA Swimming: "100 BR SCY"
                    # Relays: "200 Medley Relay" -> "200 MEDLEY RELAY SCY"
                    normalized_event = self._normalize_event_name(event_name)

                    all_swims.append(
                        {
                            "swimmer_id": metadata.get("careerId", ""),
                            "Name": swimmer_name,  # Standard: "Name"
                            "Gender": gender,  # Standard: "Gender"
                            "Age": None,  # Not available on MaxPreps
                            "grade": grade_numeric,
                            "Event": normalized_event,  # Standard: "Event"
                            "SwimTime": time,  # Standard: "SwimTime"
                            "SwimDate": date,  # Standard: "SwimDate"
                            "MeetName": meet_name,  # Standard: "MeetName"
                            "round": round_type,
                            "splits": splits,
                            "Team": school_name,  # Standard: "Team"
                            "source": "maxpreps",
                        }
                    )

        return pd.DataFrame(all_swims)

    def _normalize_event_name(self, maxpreps_event: str) -> str:
        """Normalize MaxPreps event names to USA Swimming format.

        MaxPreps uses format like "100 Breast", "200 Individual Medley"
        USA Swimming uses format like "100 BR SCY", "200 IM SCY"

        High school swimming in USA is SCY (short course yards).

        Args:
            maxpreps_event: Event name from MaxPreps (e.g., "100 Breast")

        Returns:
            Normalized event name (e.g., "100 BR SCY")
        """
        # Handle relays first (they don't follow the same pattern)
        if "Relay" in maxpreps_event:
            # "200 Free Relay" -> "200 FR RELAY SCY"
            # "200 Medley Relay" -> "200 MEDLEY RELAY SCY"
            event_upper = maxpreps_event.upper().replace(" RELAY", " RELAY SCY")
            return event_upper.replace(" FREE RELAY", " FR RELAY")

        # Stroke abbreviations mapping
        stroke_map = {
            "FREE": "FR",
            "BACK": "BK",
            "BREAST": "BR",
            "FLY": "FL",
            "BUTTERFLY": "FL",
            "INDIVIDUAL MEDLEY": "IM",
        }

        # Convert to uppercase for matching
        event_upper = maxpreps_event.upper()

        # Extract distance and stroke
        parts = event_upper.split()
        if len(parts) >= 2:
            distance = parts[0]  # e.g., "100", "200", "500"
            stroke_full = " ".join(parts[1:])  # e.g., "BREAST", "INDIVIDUAL MEDLEY"

            # Map to abbreviation
            stroke_abbr = stroke_map.get(stroke_full, stroke_full)

            # Return normalized format with SCY course
            return f"{distance} {stroke_abbr} SCY"

        # If we can't parse it, return as-is with SCY appended
        return f"{maxpreps_event} SCY"

    def validate_team_id(self, team_id: str) -> bool:
        """Validate MaxPreps school slug format.

        Args:
            team_id: School slug (e.g., "tanque-verde-hawks")

        Returns:
            True if format looks valid
        """
        # School slugs are lowercase with hyphens
        return bool(re.match(r"^[a-z0-9-]+$", team_id))

    def get_config_template(self) -> dict[str, str]:
        """Get MaxPreps configuration template."""
        return {
            "DATA_SOURCE": "maxpreps",
            "MAXPREPS_SCHOOL_SLUG": "your-school-slug",
            "MAXPREPS_STATE": "az",
            "MAXPREPS_CITY": "tucson",
            "MAXPREPS_SEASONS": "24-25,23-24,22-23",
            "CLUB_NAME": "Your High School Name",
        }

    def get_team_relays(self, seasons: list[str] | None = None) -> pd.DataFrame:
        """Fetch team relay results from MaxPreps meet results pages.

        Relays are team events (4 swimmers) and appear on team meet results,
        not on individual athlete pages.

        Args:
            seasons: List of seasons (e.g., ["24-25", "23-24"])

        Returns:
            DataFrame with columns:
                - Event: Relay event name (e.g., "200 FR RELAY SCY")
                - Gender: "M" or "F"
                - SwimTime: Relay time
                - SwimDate: Date of meet
                - MeetName: Name of meet
                - Team: School name
                - season: Season year
        """
        if seasons is None:
            seasons = self.seasons

        all_relays = []

        for season in seasons:
            # Scrape boys relays
            boys_relays = self._scrape_team_relays(self.school_slug, season, "boys")
            if not boys_relays.empty:
                boys_relays["Gender"] = "M"
                all_relays.append(boys_relays)

            # Scrape girls relays
            girls_relays = self._scrape_team_relays(self.school_slug, season, "girls")
            if not girls_relays.empty:
                girls_relays["Gender"] = "F"
                all_relays.append(girls_relays)

        if not all_relays:
            return pd.DataFrame()

        return pd.concat(all_relays, ignore_index=True)

    def _scrape_team_relays(self, school_slug: str, season: str, gender_path: str) -> pd.DataFrame:
        """Scrape relay results from team schedule/results page.

        Relays are found on individual meet result pages (contest pages).
        Navigate from schedule page to each meet's "Box Score" link.

        Args:
            school_slug: School identifier
            season: Season (e.g., "24-25")
            gender_path: "boys" or "girls"

        Returns:
            DataFrame with relay data
        """
        # Build URL for team schedule
        if gender_path == "boys":
            schedule_url = f"{self.base_url}/{self.state}/{self.city}/{school_slug}/swimming/fall/{season}/schedule/"
        else:
            schedule_url = (
                f"{self.base_url}/{self.state}/{self.city}/{school_slug}/swimming/{gender_path}/fall/{season}/schedule/"  # noqa: E501
            )

        print(f"  Fetching {gender_path} relay results: {season}")

        try:
            schedule_html = self._fetch_page(schedule_url)
        except Exception as e:
            print(f"    ⚠️  Failed to fetch {gender_path} schedule for {season}: {e}")
            return pd.DataFrame()

        # Parse schedule page
        schedule_soup = BeautifulSoup(schedule_html, "html.parser")

        all_relays = []

        # Find meet result links (look for "Box Score" links or links to /local/contest/)
        meet_links = []
        for link in schedule_soup.find_all("a", href=True):
            href = link["href"]
            # Look for contest URLs or "Box Score" text
            if "/local/contest/" in href or "contestid=" in href:
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                if full_url not in meet_links:
                    meet_links.append(full_url)

        print(f"    Found {len(meet_links)} meets with results")

        # Visit each meet result page to extract relay times
        for meet_url in meet_links:
            try:
                meet_html = self._fetch_page(meet_url, wait_time=2000)
                meet_soup = BeautifulSoup(meet_html, "html.parser")

                # Extract meet name and date from page title
                meet_name = "Unknown Meet"
                meet_date = None

                title_elem = meet_soup.find("h1")
                if title_elem:
                    meet_name = title_elem.get_text(strip=True)

                # Look for date in the page (often near title)
                # Try to find it in various places
                for meta in meet_soup.find_all(["div", "span", "p"]):
                    text = meta.get_text(strip=True)
                    # Look for date pattern like "9/14/2024"
                    date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", text)
                    if date_match:
                        meet_date = date_match.group(1)
                        break

                # Find relay event sections (200 Medley Relay, 200 Free Relay, 400 Free Relay)
                # These are usually h3 or h4 headers with "Relay" in the name
                relay_events = ["200 Medley Relay", "200 Free Relay", "400 Free Relay"]

                for relay_event in relay_events:
                    # Look for this relay event in the page
                    for heading in meet_soup.find_all(["h2", "h3", "h4"]):
                        heading_text = heading.get_text(strip=True)
                        if relay_event in heading_text:
                            # Find the results table after this heading
                            table = heading.find_next("table")
                            if not table:
                                continue

                            # Parse the table to find our school's result
                            tbody = table.find("tbody")
                            if not tbody:
                                continue

                            for row in tbody.find_all("tr"):
                                cols = row.find_all("td")
                                if len(cols) < 3:
                                    continue

                                # Columns: Place | Name | School | Round | Time (or similar)
                                # Find if this row contains our school
                                row_text = row.get_text()
                                school_pattern = f"{school_slug}".replace("-", " ")

                                if school_pattern.lower() in row_text.lower() or f"{self.city}" in row_text.lower():
                                    # Extract place and time
                                    place = cols[0].get_text(strip=True)
                                    # Time is usually in the last column or second-to-last
                                    time = cols[-1].get_text(strip=True)

                                    # If last column doesn't look like a time, try second-to-last
                                    if not re.match(r"\d+:\d+\.\d+", time) and len(cols) >= 4:
                                        time = cols[-2].get_text(strip=True)

                                    if time and re.match(r"\d+:\d+\.\d+", time):
                                        # Normalize event name
                                        normalized_event = self._normalize_event_name(relay_event)

                                        all_relays.append(
                                            {
                                                "Event": normalized_event,
                                                "SwimTime": time,
                                                "SwimDate": meet_date,
                                                "MeetName": meet_name,
                                                "Team": "Tanque Verde (Tucson, AZ)",
                                                "place": place,
                                                "season": season,
                                                "source": "maxpreps",
                                            }
                                        )
                                        print(f"      ✓ {relay_event}: {place} - {time}")

            except Exception as e:
                print(f"      ⚠️  Failed to fetch meet {meet_url}: {e}")
                continue

        return pd.DataFrame(all_relays)

    def __del__(self):
        """Cleanup Playwright resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

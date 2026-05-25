import requests
import logging
from typing import Any

from sbdots.library.logger import setup_actions_state
from sbdots.library.config_utils import get_config, set_config
from sbdots.constants import WEATHER_ICONS, WEATHER_SECTION
from ._base import BaseAction

setup_actions_state(__name__)
logger = logging.getLogger(__name__)


class GetWeatherData(BaseAction):
    def _ensure_default_credentials(self) -> None:
        """Ensure default weather credentials exist in settings"""
        logger.debug("Creating default weather credentials in settings...")
        set_config(
            "api_key",
            "your_api_key_here",
            section=WEATHER_SECTION,
            logger=logger,
        )
        set_config("latitude", "0.0", section=WEATHER_SECTION, logger=logger)
        set_config("longitude", "0.0", section=WEATHER_SECTION, logger=logger)

    def get_user_credentials(self) -> Any:
        """Load weather credentials from settings"""
        logger.debug("Loading weather credentials from settings...")

        api_key = get_config("api_key", section=WEATHER_SECTION, logger=logger)
        latitude = get_config("latitude", section=WEATHER_SECTION, logger=logger)
        longitude = get_config("longitude", section=WEATHER_SECTION, logger=logger)

        # If credentials don't exist, create defaults
        if not api_key or not latitude or not longitude:
            logger.debug(
                "Weather credentials not found in settings, creating defaults..."
            )
            self._ensure_default_credentials()
            api_key = "your_api_key_here"
            latitude = "0.0"
            longitude = "0.0"

        logger.info("User credentials loaded successfully")
        return {
            "api_key": api_key,
            "latitude": float(latitude) if latitude else 0.0,
            "longitude": float(longitude) if longitude else 0.0,
        }

    def get_weather(self) -> Any:
        """Fetch weather data from WeatherAPI.com"""
        logger.debug("Fetching weather data from WeatherAPI.com...")

        self.user_credentials = self.get_user_credentials()
        key = self.user_credentials.get("api_key")

        # Check for valid api_key
        if key == "your_api_key_here":
            logger.warning("API-Key not set, returning...")
            return None

        latitude = self.user_credentials.get("latitude")
        longitude = self.user_credentials.get("longitude")

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={latitude},{longitude}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes

            logger.info("Successfully fetched weather data from WeatherAPI.com")
            return response.json()
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except requests.HTTPError as e:
            logger.error(f"Bad status code: {e}")
            return None
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}, retry later!")
            return "timeout"
        except requests.exceptions.RequestException:
            logger.exception("Error: Unable to fetch weather data")
            return None

    def format_weather_text(self, data):
        """Format weather output for Waybar"""
        if not data:
            return "Weather Unavailable!"

        logger.debug("Formating weather output for Waybar-module-text")
        current_weather = data.get("current", {})
        temperature = current_weather.get("temp_c", "N/A")
        condition = current_weather.get("condition", {})

        # Default to Sunny if code is missing
        condition_code = condition.get("code", 1000)
        condition_text = condition.get("text", "Unknown")

        # Shorten the condition text
        condition_text = (
            condition_text[:20] + "..." if len(condition_text) > 20 else condition_text
        )

        # Round the temperature to the nearest integer
        if isinstance(temperature, (int, float)):
            temperature = int(round(temperature))

        # Get the icon based on the condition code
        # Default to Sunny if code is unknown
        icon = WEATHER_ICONS.get(condition_code, "󰖨")

        return f"{icon} {condition_text}, {temperature}°C"

    def format_weather_tooltip(self, data) -> str:
        """Format tooltip with more detailed information"""

        if not data:
            return "Invalid Credentials! \nPlease update your API key and location in ~/.sbdots/setting.ini [Weather] section"

        logger.debug("Formating weather output for Waybar-module-tooltip")
        tooltip = "Weather information"
        location = data.get("location", {})
        location_name = location.get("name", "Unknown")
        location_region = location.get("region", "Unknown")
        location_country = location.get("country", "Unknown")
        location_line = (
            f"Location: {location_name}, {location_region} - {location_country}"
        )

        current_weather = data.get("current", {})
        tooltip = f"{location_line}\n"
        tooltip += f"Temperature: {current_weather.get('temp_c', 'N/A')}°C\n"
        tooltip += (
            f"Condition: {current_weather.get('condition', {}).get('text', 'N/A')}\n"
        )
        tooltip += f"Wind Speed: {current_weather.get('wind_kph', 'N/A')} km/h\n"
        tooltip += f"Wind Direction: {current_weather.get('wind_degree', 'N/A')}°\n"
        tooltip += f"Humidity: {current_weather.get('humidity', 'N/A')}%"

        return tooltip

    def main(self):
        self.user_credentials: Any = self.get_user_credentials()
        weather_data = self.get_weather()
        text, tooltip = "Timeout Error!", "Retry Later!"

        if not weather_data == "timeout":
            text = self.format_weather_text(weather_data)
            tooltip = self.format_weather_tooltip(weather_data)

        logger.debug("Sending weather output for Waybar-module")
        self.send({"text": text, "tooltip": tooltip})

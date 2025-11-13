import requests
import json
from pathlib import Path
from typing import Dict, Any

from utils.logger import Logger
from utils.paths import SBDOTS_LOG_DIR, SBDOTS_CONFIG_DIR


# Map: WeatherAPI.com condition codes > Nerd Fonts icons
ICONS: Dict[int, str] = {
    1000: "󰖨",  # Sunny
    1003: "󰖕",  # Partly cloudy
    1006: "󰖐",  # Cloudy
    1009: "󰖑",  # Overcast
    1030: "󰖑",  # Mist
    1063: "󰼳",  # Patchy rain possible
    1066: "󰼴",  # Patchy snow possible
    1069: "󰙿",  # Patchy sleet possible
    1072: "󰙿",  # Patchy freezing drizzle possible
    1087: "󰙾",  # Thundery outbreaks possible
    1114: "󰼶",  # Blowing snow
    1117: "󰼶",  # Blizzard
    1135: "󰖑",  # Fog
    1147: "󰖑",  # Freezing fog
    1150: "󰖗",  # Patchy light drizzle
    1153: "󰖗",  # Light drizzle
    1168: "󰖗",  # Freezing drizzle
    1171: "󰖗",  # Heavy freezing drizzle
    1180: "󰖗",  # Patchy light rain
    1183: "󰖗",  # Light rain
    1186: "󰖗",  # Moderate rain at times
    1189: "󰖗",  # Moderate rain
    1192: "󰖗",  # Heavy rain at times
    1195: "󰖗",  # Heavy rain
    1198: "󰖗",  # Light freezing rain
    1201: "󰖗",  # Moderate or heavy freezing rain
    1204: "󰙿",  # Light sleet
    1207: "󰙿",  # Moderate or heavy sleet
    1210: "󰼶",  # Patchy light snow
    1213: "󰼶",  # Light snow
    1216: "󰼶",  # Moderate snow
    1219: "󰼶",  # Heavy snow
    1222: "󰙿",  # Ice pellets
    1225: "󰙿",  # Light ice pellets
    1237: "󰙿",  # Moderate or heavy ice pellets
    1240: "󰖗",  # Light rain shower
    1243: "󰖗",  # Moderate or heavy rain shower
    1246: "󰖗",  # Torrential rain shower
    1249: "󰙿",  # Light sleet showers
    1252: "󰙿",  # Moderate or heavy sleet showers
    1255: "󰼶",  # Light snow showers
    1258: "󰼶",  # Moderate or heavy snow showers
    1261: "󰙿",  # Light showers of ice pellets
    1264: "󰙿",  # Moderate or heavy showers of ice pellets
    1273: "󰙾",  # Patchy light rain with thunder
    1276: "󰙾",  # Moderate or heavy rain with thunder
    1279: "󰙾",  # Patchy light snow with thunder
    1282: "󰙾",  # Moderate or heavy snow with thunder
}


class OnGetWeather:
    def __init__(self, conn, *args) -> None:
        # Create logfile and setup logging
        self.logfile: Path = SBDOTS_LOG_DIR / "on_get_weather.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)
        self.logger = Logger(log_file=self.logfile)

        self.conn = conn

        self.logger.debug("Parsing user credentials...")
        self.user_credentials: Any = self.get_user_credentials()

    def get_user_credentials(self) -> Any:
        self.user_credentials_file: Path = (
            SBDOTS_CONFIG_DIR / "settings" / "weather_api.json"
        )
        data = {}

        if not self.user_credentials_file.exists():
            self.logger.debug(f"User credentials file '{self.user_credentials_file}' not found!")
            self.logger.debug("Creating a template user credentials file")
            self.user_credentials_file.parent.mkdir(parents=True, exist_ok=True)
            self.user_credentials_file.touch(exist_ok=True)
            text: str = """
{
    "api_key": "your_api_key_here",
    "latitude": 0.0,
    "longitude": 0.0
}"""
            self.user_credentials_file.write_text(text, encoding="utf-8")

        try:
            with self.user_credentials_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {self.user_credentials_file}: {e}")
        else:
            self.logger.info("User Credentials loaded successfully")

        return data

    def get_weather(self) -> Any:
        """Fetch weather data from WeatherAPI.com"""
        self.logger.debug("Fetching weather data from WeatherAPI.com...")
        
        key = self.user_credentials.get("api_key")
        
        # Check for valid api_key
        if key == "your_api_key_here":
            self.logger.warning("API-Key not set, returning...")
            return None
        
        latitude = self.user_credentials.get("latitude")
        longitude = self.user_credentials.get("longitude")

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={latitude},{longitude}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            
            self.logger.info("Successfully fetched weather data from WeatherAPI.com")
            return response.json()
        except requests.HTTPError as e:
            self.logger.error(f"Bad status code. {e}")
            return None
        except requests.Timeout as e:
            self.logger.error(f"Request timeout: {e}, retry later!")
            return "timeout"
        except requests.exceptions.RequestException:
            self.logger.exception("Error: Unable to fetch weather data")
            return None

    def format_weather_text(self, data):
        """Format weather output for Waybar"""
        if not data:
            return "Weather Unavailable!"

        self.logger.debug("Formating weather output for Waybar-module-text")
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
        icon = ICONS.get(condition_code, "󰖨")

        return f"{icon} {condition_text}, {temperature}°C"

    def format_weather_tooltip(self, data) -> str:
        """Format tooltip with more detailed information"""
        
        if not data:
            return f"Invalid Credentials! \nPlease put correct credentials in: \n  {self.user_credentials_file}"

        self.logger.debug("Formating weather output for Waybar-module-tooltip")
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
        weather_data = self.get_weather()
        text, tooltip = "Timeout Error!", "Retry Later!"

        if not weather_data == "timeout":
            text = self.format_weather_text(weather_data)
            tooltip = self.format_weather_tooltip(weather_data)

        try:
            self.logger.debug("Sending weather output for Waybar-module")
            self.conn.sendall(b"\n")
            self.conn.sendall(
                (json.dumps({"text": text, "tooltip": tooltip}) + "\n").encode("utf-8")
            )
        except (BrokenPipeError, ConnectionResetError, OSError):
            self.logger.exception("Error while sending data.")
            pass

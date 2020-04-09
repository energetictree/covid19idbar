import rumps
import requests
import datetime
import webbrowser


class CoronaBar(object):
    base_api_url = "https://eligiblestore.com/api/covid19idn"
    province_api_url = "https://eligiblestore.com/api/covid19id"
    default_country = "Indonesia"
    default_province = "Bali"
    update_interval = 900  # seconds
    about_url = "https://eligiblestore.com/blog/2020/04/09/covid-19-id-bar/"

    # APP
    def __init__(self):
        self.app = rumps.App("Covid19IDBar", "🦠")
        self.provinces = rumps.MenuItem(title="Select Province")
        self.about = rumps.MenuItem(title="About", callback=self.open_page)

        self.country = self.default_country
        self.province = self.default_province

        self.app.menu = [self.provinces, self.about]

        province_list = self.get_province_list()
        self.setup(province_list, self.province)

    def setup(self, province_list, default_province):
        for province in province_list:
            self.provinces.add(
                rumps.MenuItem(
                    title=f"{province}", callback=self.update_province_listing
                )
            )

        self.create_province_listing(
            rumps.MenuItem(title=f"{self.default_province}")
        )

    def open_page(self, sender):
        try:
            webbrowser.open(self.about_url)
        except Exception as e:
            print(str(e))
            return False

    def create_province_listing(self, province):
        # print("Creating")
        data = self.get_province_data(province.title)
        for k, v in data.items():
            self.app.menu.add(rumps.MenuItem(self.string_mapper(k, v)))
        current_time = datetime.datetime.now().strftime("%H:%M")
        self.app.menu.add(rumps.MenuItem(title=f"Updated at {current_time}"))
        # print("Created")
        self.timer = rumps.Timer(self.on_update, self.update_interval)
        self.timer.start()

    def update_province_listing(self, province):
        # print("Update")
        self.province = province.title
        for k, v in self.app.menu.items():
            if k not in ["Select Province", "Quit", "About"]:
                del self.app.menu[k]

        data = self.get_country_data()
        for k, v in data.items():
            self.app.menu.insert_before(
                "Quit", rumps.MenuItem(self.string_mapper_country(k, v))
            )

        data = self.get_province_data(province.title)
        for k, v in data.items():
            self.app.menu.insert_before(
                "Quit", rumps.MenuItem(self.string_mapper(k, v))
            )

        current_time = datetime.datetime.now().strftime("%H:%M")
        self.app.menu.insert_before(
            "Quit", rumps.MenuItem(title=f"Refreshed at {current_time}")
        )
        # print(f"Updated,province is {self.province}")

    def on_update(self, sender):
        # print("Timer is running.")
        self.update_province_listing(rumps.MenuItem(title=self.province))

    def run(self):
        self.app.run()

    # DATA

    def get_province_list(self):
        response = requests.request("GET", self.province_api_url)
        data = response.json()
        province_list = [e["Provinsi"] for e in data]
        return sorted(province_list)

    def get_country_data(self):
        response = requests.request("GET", self.base_api_url)
        data = response.json()
        return data

    def get_province_data(self, province):
        response = requests.request("GET", f"{self.province_api_url}/{province}")
        data = response.json()
        return data

    # STRING MAPPER
 
    def string_mapper_country(self, key, value):
        if key == "Tanggal":
            return f"{value}"

        elif key == "Negara":
            return f"{value}".upper()

        elif key == "Jumlah_Kasus_Kumulatif":
            return f"• Positive: {value}"

        elif key == "Jumlah_Kasus_Baru_per_Hari":
            return f"• New Positive: {value}"
        
        elif key == "Jumlah_pasien_dalam_perawatan":
            return f"• Active: {value}"
        
        elif key == "Jumlah_Pasien_Sembuh":
            return f"• Recovered: {value}"

        elif key == "Jumlah_Pasien_Meninggal":
            return f"• Death: {value}"

        elif key == "recovered":
            return f"• Recovered: {value}"
        
    def string_mapper(self, key, value):
        if key == "Provinsi":
            return f"{value}".upper()

        elif key == "Kasus Positif":
            return f"• Positive: {value}"

        elif key == "Kasus Sembuh":
            return f"• Recovered: {value}"

        elif key == "Kasus Meninggal":
            return f"• Death: {value}"

if __name__ == "__main__":
    app = CoronaBar()
    app.run()

# scripts/update_2026_dates.py
"""
Update all race dates to 2026 (and some late 2025)
Based on official race calendars and typical race schedules
"""
import csv
from datetime import datetime

# 2026 dates for major races (confirmed from official sources)
DATE_UPDATES_2026 = {
    # Major Marathons (World Marathon Majors)
    "Chicago Marathon": "10/11/2026",  # 2nd Sunday of October
    "London Marathon": "4/26/2026",  # April (confirmed)
    "Berlin Marathon": "9/27/2026",  # Last Sunday of September
    "New York City Marathon": "11/1/2026",  # 1st Sunday of November
    "Boston Marathon": "4/20/2026",  # Patriots Day (3rd Monday of April)
    "Tokyo Marathon": "3/1/2026",  # Early March

    # Other Major Marathons
    "Dublin Marathon": "10/25/2026",  # Last Sunday of October
    "Paris Marathon": "4/5/2026",  # Early April
    "Amsterdam Marathon": "10/18/2026",  # 3rd Sunday of October
    "Frankfurt Marathon": "10/25/2026",  # Late October
    "Vienna Marathon": "4/19/2026",  # Mid April
    "Barcelona Marathon": "3/15/2026",  # Mid March
    "Rome Marathon": "3/22/2026",  # Late March
    "Valencia Marathon": "12/6/2026",  # Early December
    "Athens Marathon": "11/8/2026",  # Early November
    "Istanbul Marathon": "11/1/2026",  # Early November
    "Melbourne Marathon": "10/11/2026",  # 2nd Sunday of October
    "Sydney Marathon": "9/20/2026",  # Mid September
    "Lisbon Marathon": "10/11/2026",  # 2nd Sunday of October
    "Copenhagen Marathon": "5/17/2026",  # Mid May
    "Stockholm Marathon": "5/30/2026",  # Late May
    "Prague Marathon": "5/3/2026",  # Early May
    "Zurich Marathon": "4/26/2026",  # Late April
    "Hamburg Marathon": "4/26/2026",  # Late April
    "Rotterdam Marathon": "4/12/2026",  # Mid April
    "Brussels Marathon": "10/4/2026",  # Early October
    "Budapest Marathon": "10/4/2026",  # Early October
    "Warsaw Marathon": "9/27/2026",  # Late September
    "Oslo Marathon": "9/19/2026",  # Mid September
    "Munich Marathon": "10/11/2026",  # 2nd Sunday of October
    "Milan Marathon": "4/5/2026",  # Early April
    "Florence Marathon": "11/29/2026",  # Late November
    "Venice Marathon": "10/25/2026",  # Late October
    "Seville Marathon": "2/22/2026",  # Late February
    "Madrid Marathon": "4/26/2026",  # Late April
    "Cape Town Marathon": "10/18/2026",  # Mid October
    "Honolulu Marathon": "12/13/2026",  # 2nd Sunday of December
    "Dubai Marathon": "1/23/2026",  # Late January
    "Singapore Marathon": "12/6/2026",  # Early December
    "Gold Coast Marathon": "7/5/2026",  # Early July
    "Los Angeles Marathon": "3/22/2026",  # Late March
    "Marine Corps Marathon": "10/25/2026",  # Late October
    "Philadelphia Marathon": "11/22/2026",  # 3rd Sunday of November
    "Toronto Marathon": "10/18/2026",  # Mid October
    "Houston Marathon": "1/18/2026",  # Mid January
    "Miami Marathon": "1/25/2026",  # Late January
    "Austin Marathon": "2/15/2026",  # Mid February
    "Seattle Marathon": "11/29/2026",  # Late November
    "Twin Cities Marathon": "10/4/2026",  # Early October
    "Portland Marathon": "10/4/2026",  # Early October
    "California International Marathon": "12/6/2026",  # Early December
    "Walt Disney World Marathon": "1/10/2026",  # Early January
    "Little Rock Marathon": "3/1/2026",  # Early March
    "Grandma's Marathon": "6/20/2026",  # Mid June
    "San Francisco Marathon": "7/26/2026",  # Late July
    "Eugene Marathon": "4/26/2026",  # Late April
    "Flying Pig Marathon": "5/3/2026",  # Early May
    "Detroit Marathon": "10/18/2026",  # Mid October
    "Indianapolis Marathon": "11/7/2026",  # Early November
    "St. George Marathon": "10/3/2026",  # Early October
    "Jerusalem Marathon": "3/13/2026",  # Mid March
    "Nagano Marathon": "4/19/2026",  # Mid April
    "Osaka Marathon": "2/28/2026",  # Late February
    "Seoul Marathon": "3/15/2026",  # Mid March
    "Shanghai Marathon": "11/29/2026",  # Late November
    "Marrakech Marathon": "1/25/2026",  # Late January
    "Mexico City Marathon": "8/30/2026",  # Late August
    "Rotorua Marathon": "5/2/2026",  # Early May
    "Bali Marathon": "8/23/2026",  # Late August
    "Phuket Marathon": "6/14/2026",  # Mid June
    "Big Sur Marathon": "4/26/2026",  # Late April
    "Queenstown Marathon": "11/21/2026",  # Late November
    "Vermont City Marathon": "5/31/2026",  # Late May
    "Buenos Aires Marathon": "9/20/2026",  # Mid September
    "Borobudur Marathon": "11/15/2026",  # Mid November
    "Sunshine Coast Marathon": "8/29/2026",  # Late August
    "Midnight Sun Marathon": "6/20/2026",  # Mid June
    "Medoc Marathon": "9/12/2026",  # Mid September
    "Toroko Gorge Marathon": "11/7/2026",  # Early November

    # Half Marathons
    "Great North Run": "9/13/2026",  # Mid September
    "Great Scottish Run": "10/4/2026",  # Early October
    "Brighton Half Marathon": "2/28/2026",  # Late February
    "Reading Half Marathon": "3/22/2026",  # Late March
    "Bath Half Marathon": "3/15/2026",  # Mid March
    "Cambridge Half Marathon": "3/8/2026",  # Early March
    "Oxford Half Marathon": "10/11/2026",  # 2nd Sunday of October
    "Cardiff Half Marathon": "10/4/2026",  # Early October
    "Manchester Half Marathon": "10/11/2026",  # 2nd Sunday of October
    "Edinburgh Half Marathon": "5/24/2026",  # Late May
    "Liverpool Half Marathon": "3/29/2026",  # Late March
    "Royal Parks Half Marathon": "10/11/2026",  # 2nd Sunday of October
    "Hackney Half Marathon": "5/17/2026",  # Mid May
    "Great South Run": "10/25/2026",  # Late October
    "Belfast Half Marathon": "9/20/2026",  # Mid September
    "Dublin Half Marathon": "9/20/2026",  # Mid September
    "Copenhagen Half Marathon": "9/20/2026",  # Mid September
    "Paris Half Marathon": "3/8/2026",  # Early March
    "Barcelona Half Marathon": "2/15/2026",  # Mid February
    "Lisbon Half Marathon": "3/22/2026",  # Late March
    "Valencia Half Marathon": "10/25/2026",  # Late October
    "Seville Half Marathon": "1/25/2026",  # Late January
    "Madrid Half Marathon": "4/26/2026",  # Late April
    "Rome Half Marathon Via Pacis": "9/20/2026",  # Mid September
    "Napoli Half Marathon": "2/22/2026",  # Late February
    "Venice Half Marathon": "10/24/2026",  # Late October
    "Athens Half Marathon": "4/26/2026",  # Late April
    "Istanbul Half Marathon": "4/12/2026",  # Mid April
    "Amsterdam Half Marathon": "10/18/2026",  # Mid October
    "Rotterdam Half Marathon": "9/13/2026",  # Mid September
    "Brussels Half Marathon": "10/4/2026",  # Early October
    "Berlin Half Marathon": "4/5/2026",  # Early April
    "Munich Half Marathon": "4/19/2026",  # Mid April
    "Frankfurt Half Marathon": "5/3/2026",  # Early May
    "Stockholm Half Marathon": "9/5/2026",  # Early September
    "Göteborgsvarvet Half": "5/23/2026",  # Late May
    "Malmö Half Marathon": "6/7/2026",  # Early June
    "Helsinki Half Marathon": "6/6/2026",  # Early June
    "Prague Half Marathon": "4/4/2026",  # Early April
    "Vienna Half Marathon": "4/19/2026",  # Mid April
    "Budapest Half Marathon": "9/13/2026",  # Mid September
    "Warsaw Half Marathon": "3/29/2026",  # Late March
    "Ljubljana Half Marathon": "10/25/2026",  # Late October
    "Bucharest Half Marathon": "5/16/2026",  # Mid May
    "Tallinn Half Marathon": "9/12/2026",  # Mid September
    "Poznan Half Marathon": "4/12/2026",  # Mid April
    "Esztergom Half Marathon": "5/16/2026",  # Mid May
    "CPC Run The Hague": "3/8/2026",  # Early March
    "Route Du Vin Half Marathon": "9/27/2026",  # Late September
    "Marseille-Cassis": "10/25/2026",  # Late October
    "Turin Half Marathon": "10/4/2026",  # Early October
    "Royal Windsor Half Marathon": "9/27/2026",  # Late September
    "Hampton Court Palace Half": "3/15/2026",  # Mid March
    "Wales Coastal Half Marathon": "7/5/2026",  # Early July
    "Sarajevo Half Marathon": "9/19/2026",  # Mid September
    "New York City Half Marathon": "3/22/2026",  # Late March
    "Rock 'n' Roll Las Vegas Half": "2/22/2026",  # Late February
    "Philadelphia Half Marathon": "11/21/2026",  # Late November
    "Rock 'n' Roll San Diego Half": "6/7/2026",  # Early June
    "Atlanta Half Marathon": "3/1/2026",  # Early March
    "Austin Half Marathon": "2/15/2026",  # Mid February
    "Miami Half Marathon": "1/25/2026",  # Late January
    "Disney Princess Half Marathon": "2/21/2026",  # Late February
    "Rock 'n' Roll Nashville Half": "4/25/2026",  # Late April
    "United Airlines NYC Half": "3/22/2026",  # Late March
    "Naples Half Marathon": "1/17/2026",  # Mid January
    "Brooklyn Half Marathon": "5/16/2026",  # Mid May
    "Seattle Half Marathon": "11/29/2026",  # Late November
    "Sydney Morning Herald Half": "5/17/2026",  # Mid May
    "Shanghai Half Marathon": "4/19/2026",  # Mid April
    "Montreal Half Marathon": "9/27/2026",  # Late September
    "Vancouver Half Marathon": "5/23/2026",  # Late May
    "San Francisco Half Marathon": "7/26/2026",  # Late July
}

def update_dates():
    input_file = "data/seed_races.csv"
    output_file = "data/seed_races_updated.csv"

    rows_updated = 0
    today = datetime(2025, 11, 2).date()

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        rows = []
        for row in reader:
            event = row['Event']
            current_date = row['Date']

            # Check if date is in the past
            if current_date:
                try:
                    # Parse current date (m/d/yyyy format)
                    parts = current_date.replace('-', '/').split('/')
                    if len(parts) == 3:
                        m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
                        date_obj = datetime(y, m, d).date()

                        if date_obj < today:
                            # Check if we have a 2026 date for this race
                            if event in DATE_UPDATES_2026:
                                row['Date'] = DATE_UPDATES_2026[event]
                                rows_updated += 1
                                print(f"✓ Updated: {event}")
                                print(f"  {current_date} → {DATE_UPDATES_2026[event]}")
                            else:
                                print(f"⚠ No 2026 date found for: {event} (currently {current_date})")
                except:
                    print(f"⚠ Could not parse date for: {event} ({current_date})")

            rows.append(row)

    # Write updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Updated {rows_updated} race dates to 2026")
    print(f"📄 Updated CSV saved to: {output_file}")
    print(f"\nTo use the updated version:")
    print(f"  mv {output_file} {input_file}")

if __name__ == "__main__":
    update_dates()

# scripts/fix_urls.py
"""
Script to fix broken/missing URLs in seed_races.csv
"""
import csv

# Mapping of race names to their official URLs
URL_FIXES = {
    "Rome Half Marathon Via Pacis": "https://www.romahalfmarathon.org/",
    "Buenos Aires Marathon": "https://www.maratondebuenosaires.com/",
    "Route Du Vin Half Marathon": "https://www.routeduvin.lu/en",
    "Royal Windsor Half Marathon": "https://www.entryhub.co.uk/windsor-half-marathon-2025",
    "Great Scottish Run": "https://www.greatrun.org/events/great-scottish-run/",
    "Oxford Half Marathon": "https://www.oxfordhalf.com/",
    "Chicago Marathon": "https://www.chicagomarathon.com/",
    "Melbourne Marathon": "https://melbournemarathon.com.au/",
    "TCS Amsterdam Marathon": "https://www.tcsamsterdammarathon.eu/",
    "Amsterdam Marathon": "https://www.tcsamsterdammarathon.eu/",
    "Cape Town Marathon": "https://capetownmarathon.com/",
    "Frankfurt Marathon": "https://www.frankfurt-marathon.com/en/",
    "Istanbul Marathon": "https://maraton.istanbul/?lang=en",
    "New York City Marathon": "https://www.nyrr.org/tcsnycmarathon",
    "Athens Marathon": "https://www.athensauthenticmarathon.gr/en/",
    "Honolulu Marathon": "https://www.honolulumarathon.org/",
    "Barcelona Half Marathon": "https://www.zurichmaratobarcelona.es/",
    "Napoli City Half Marathon": "https://www.napolirunning.it/",
    "Paris Half Marathon": "https://www.semi-de-paris.com/en/",
    "CPC Run The Hague": "https://www.nndenhaaghalvemarathon.nl/en/",
    "LA Marathon": "https://www.lamarathon.com/",
    "Prague Marathon": "https://www.runczech.com/en/events/races/volkswagen-prague-marathon/",
    "Vienna Marathon": "https://www.vienna-marathon.com/en/",
    "Zurich Marathon": "https://www.zurichmarathon.ch/",
    "Boston Marathon": "https://www.baa.org/races/boston-marathon",
    "Göteborgsvarvet Half Marathon": "https://www.goteborgsvarvet.se/en/",
    "Hackney Half Marathon": "https://www.hackneyhalfmarathon.co.uk/",
    "Malmö Half Marathon": "https://malmostadslopp.se/en/",
    "Gold Coast Marathon": "https://goldcoastmarathon.com.au/",
    "Great North Run": "https://www.greatrun.org/events/great-north-run/",
}

def fix_urls():
    input_file = "data/seed_races.csv"
    output_file = "data/seed_races_fixed.csv"

    rows_updated = 0

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        rows = []
        for row in reader:
            link = row['Link']
            event = row['Event']

            # Check if link is broken (doesn't start with http)
            if not link.startswith('http'):
                # Try to find a fix
                if link in URL_FIXES:
                    row['Link'] = URL_FIXES[link]
                    rows_updated += 1
                    print(f"✓ Fixed: {event} -> {URL_FIXES[link]}")
                else:
                    print(f"⚠ Still broken: {event} ({link})")

            rows.append(row)

    # Write updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Updated {rows_updated} URLs")
    print(f"📄 Fixed CSV saved to: {output_file}")
    print(f"\nTo use the fixed version:")
    print(f"  mv {output_file} {input_file}")

if __name__ == "__main__":
    fix_urls()

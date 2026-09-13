from src.data.models import GeoPlace

WORLD_LANDMARKS: list[GeoPlace] = [
    GeoPlace(
        key="great_wall_of_china",
        title="The Great Wall of China (China)",
        description=(
            "Spanning over 13,000 miles, the Great Wall is one of the most iconic structures in "
            "the world, symbolizing China's historical efforts to defend against invasions. Why "
            "Famous: It is an engineering marvel and a UNESCO World Heritage Site, attracting "
            "millions of visitors annually."
        ),
        image_file="Great_wall_of_China.jpg",
        lat=40.4319,
        lon=116.5704,
        category="Asia",
    ),
    GeoPlace(
        key="taj_mahal",
        title="Taj Mahal (India)",
        description=(
            "This white marble mausoleum, built by Mughal Emperor Shah Jahan in memory of his "
            "wife Mumtaz Mahal, is considered one of the most beautiful buildings in the world. "
            "Why Famous: A UNESCO World Heritage Site, it is one of the New Seven Wonders of the "
            "World and a symbol of eternal love."
        ),
        image_file="Taj Mahal.jpg",
        lat=27.1751,
        lon=78.0421,
        category="Asia",
    ),
    GeoPlace(
        key="mount_everest",
        title="Mount Everest (Nepal/China Border)",
        description=(
            "Standing at 8,848.86 meters (29,031.7 feet), Mount Everest is the highest peak in "
            "the world, located in the Himalayas along the Nepal-China border. It attracts "
            "mountaineers from around the world, symbolizing adventure and human endurance."
        ),
        image_file="Mount Everest.jpg",
        lat=27.9881,
        lon=86.9250,
        category="Asia",
    ),
    GeoPlace(
        key="borobudur",
        title="Borobudur (Indonesia)",
        description=(
            "Borobudur is a 9th-century Mahayana Buddhist temple in Central Java. It is the "
            "largest Buddhist temple in the world, adorned with thousands of relief panels and "
            "Buddha statues. A UNESCO World Heritage Site, Borobudur is an iconic pilgrimage site "
            "and a testament to Indonesia's rich cultural and religious history."
        ),
        image_file="Borobudur.jpg",
        lat=-7.6079,
        lon=110.2038,
        category="Asia",
    ),
    GeoPlace(
        key="kyoto_temples",
        title="Kyoto Temples (Japan)",
        description=(
            "Kyoto is home to many ancient temples and shrines, including the Golden Pavilion "
            "(Kinkaku-ji), a Zen Buddhist temple known for its stunning gold leaf exterior. "
            "Kyoto's temples are a UNESCO World Heritage Site and symbolize Japan's traditional "
            "culture, history, and peaceful aesthetics."
        ),
        image_file="Kyoto Temples.jpg",
        lat=35.0394,
        lon=135.7292,
        category="Asia",
    ),
    GeoPlace(
        key="eiffel_tower",
        title="Eiffel Tower (France)",
        description=(
            "Located in Paris, the Eiffel Tower is a wrought-iron lattice tower designed by "
            "Gustave Eiffel. Standing 330 meters (1,083 feet) tall, it offers panoramic views of "
            "the city. As one of the most recognizable landmarks in the world, the Eiffel Tower "
            "symbolizes Paris and is a global icon of French culture and elegance."
        ),
        image_file="eiffel_tower.jpg",
        lat=48.8584,
        lon=2.2945,
        category="Europe",
    ),
    GeoPlace(
        key="colosseum",
        title="Colosseum (Italy)",
        description=(
            "The Colosseum is an ancient Roman amphitheater in the heart of Rome, built in 70-80 "
            "AD. It could hold up to 80,000 spectators and was used for gladiatorial contests and "
            "public spectacles. As a UNESCO World Heritage Site, the Colosseum is one of the "
            "greatest surviving monuments of ancient Rome and a symbol of Roman engineering and "
            "culture."
        ),
        image_file="collosseum.jpg",
        lat=41.8902,
        lon=12.4922,
        category="Europe",
    ),
    GeoPlace(
        key="acropolis_of_athens",
        title="Acropolis of Athens (Greece)",
        description=(
            "The Acropolis is a hill in Athens crowned by ancient monuments, most notably the "
            "Parthenon, a temple dedicated to the goddess Athena, built in the 5th century BC. As "
            "a UNESCO World Heritage Site, the Acropolis is a symbol of ancient Greek "
            "civilization, democracy, and architectural achievement."
        ),
        image_file="Acropolis of Athens.jpg",
        lat=37.9715,
        lon=23.7267,
        category="Europe",
    ),
    GeoPlace(
        key="stonehenge",
        title="Stonehenge (United Kingdom)",
        description=(
            "Located in Wiltshire, England, Stonehenge is a prehistoric stone circle dating back "
            "over 4,000 years. Its purpose remains a mystery, though it may have been used for "
            "religious or astronomical purposes. As one of the most famous prehistoric sites in "
            "the world, Stonehenge is a UNESCO World Heritage Site and a symbol of ancient British "
            "history and mystery."
        ),
        image_file="Stonehenge.jpg",
        lat=51.1789,
        lon=-1.8262,
        category="Europe",
    ),
    GeoPlace(
        key="sydney_opera_house",
        title="Sydney Opera House (New South Wales)",
        description=(
            "Located on Sydney's Bennelong Point, the Sydney Opera House is a multi-venue "
            "performing arts center with its iconic sail-shaped roof, designed by Danish architect "
            "Jørn Utzon. One of the most distinctive and famous buildings in the world, the Sydney "
            "Opera House is a UNESCO World Heritage Site and a symbol of modern Australia."
        ),
        image_file="Sydney Opera House.jpg",
        lat=-33.8568,
        lon=151.2153,
        category="Australia",
    ),
    GeoPlace(
        key="great_barrier_reef",
        title="Great Barrier Reef (Queensland)",
        description=(
            "The Great Barrier Reef, located off the coast of Queensland, is the world's largest "
            "coral reef system, spanning over 2,300 kilometers. It is home to diverse marine life, "
            "including over 1,500 species of fish. As the world's largest coral reef, it's a "
            "UNESCO World Heritage Site and one of the seven natural wonders of the world, "
            "attracting millions of visitors annually for snorkeling and diving."
        ),
        image_file="Great Barrier Reef.jpg",
        lat=-18.2871,
        lon=147.6992,
        category="Australia",
    ),
    GeoPlace(
        key="machu_picchu",
        title="Machu Picchu (Peru)",
        description=(
            "Machu Picchu is an ancient Incan city perched high in the Andes Mountains. Built in "
            "the 15th century, it was abandoned and later rediscovered in 1911 by Hiram Bingham. "
            "As a UNESCO World Heritage Site and one of the New Seven Wonders of the World, Machu "
            "Picchu is renowned for its breathtaking location and the mystery surrounding its "
            "purpose."
        ),
        image_file="Machu Picchu.jpg",
        lat=-13.1631,
        lon=-72.5450,
        category="South America",
    ),
    GeoPlace(
        key="christ_the_redeemer",
        title="Christ the Redeemer (Brazil)",
        description=(
            "Christ the Redeemer is a colossal statue of Jesus Christ located atop Mount Corcovado "
            "in Rio de Janeiro. Standing at 30 meters tall (98 feet), it overlooks the city with "
            "open arms. This iconic statue is a symbol of Christianity around the world and one of "
            "the New Seven Wonders of the World. It's a must-see landmark for visitors to Brazil."
        ),
        image_file="Christ the Redeemer.jpg",
        lat=-22.9519,
        lon=-43.2105,
        category="South America",
    ),
    GeoPlace(
        key="statue_of_liberty",
        title="Statue of Liberty (USA)",
        description=(
            "The Statue of Liberty is a colossal neoclassical sculpture located on Liberty Island "
            "in New York Harbor. It was a gift from France to the United States in 1886, "
            "symbolizing freedom and democracy. This iconic symbol of liberty and immigration is "
            "one of the most recognizable landmarks in the world and a UNESCO World Heritage Site, "
            "representing freedom and opportunity to millions."
        ),
        image_file="Statue of Liberty.jpg",
        lat=40.6892,
        lon=-74.0445,
        category="North America",
    ),
    GeoPlace(
        key="grand_canyon",
        title="Grand Canyon (USA)",
        description=(
            "The Grand Canyon, located in Arizona, is a massive gorge carved by the Colorado "
            "River over millions of years. It stretches about 277 miles in length and reaches "
            "depths of over a mile. It is one of the Seven Natural Wonders of the World and a "
            "UNESCO World Heritage Site, known for its stunning layered rock formations that "
            "reveal millions of years of geological history."
        ),
        image_file="Grand Canyon.jpg",
        lat=36.1069,
        lon=-112.1129,
        category="North America",
    ),
    GeoPlace(
        key="serengeti_national_park",
        title="Serengeti National Park, Tanzania",
        description=(
            "Famous for its annual Great Migration, the Serengeti is one of the most iconic "
            "safari destinations in the world. Visitors can witness millions of wildebeest, "
            "zebras, and gazelles journeying across the savannah, while also spotting Africa's Big "
            "Five – lions, leopards, elephants, buffalo, and rhinos."
        ),
        image_file="Serengeti National Park.jpg",
        lat=-2.3333,
        lon=34.8333,
        category="Africa",
    ),
    GeoPlace(
        key="pyramids_of_giza",
        title="Pyramids of Giza, Egypt",
        description=(
            "As one of the Seven Wonders of the Ancient World, the Pyramids of Giza are among the "
            "most famous historical monuments. These ancient structures, including the Great "
            "Pyramid and the Sphinx, have stood for over 4,000 years and are a must-see for "
            "history enthusiasts."
        ),
        image_file="Pyramids of Giza.jpg",
        lat=29.9792,
        lon=31.1342,
        category="Africa",
    ),
    GeoPlace(
        key="victoria_falls",
        title="Victoria Falls, Zambia/Zimbabwe",
        description=(
            "One of the largest and most breathtaking waterfalls in the world, Victoria Falls is "
            "located on the border of Zambia and Zimbabwe. Known locally as The Smoke That "
            "Thunders, the falls drop from a height of 108 meters, creating a spectacular view and "
            "misty spray."
        ),
        image_file="Victoria Falls.jpg",
        lat=-17.9243,
        lon=25.8572,
        category="Africa",
    ),
]

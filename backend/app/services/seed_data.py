from datetime import datetime, timezone, timedelta
import logging
from bson import ObjectId
from app.database import get_db
from app.utils.security import hash_password

logger = logging.getLogger("seed_data")

GURGAON_SOHNA_ITEMS = [
    {
        "cook": "Anita Sharma",
        "email": "anita.sohna@gharse-demo.app",
        "locality": "Sohna Road, Sector 49, Gurgaon",
        "lat": 28.4112, "lng": 77.0435,
        "name": "Maa ke Haath ka Slow-Cooked Rajma Chawal",
        "description": "Slow-cooked Jammu rajma in a thick onion-tomato masala infused with crushed ginger and pure desi ghee, served alongside fragrant steamed basmati rice and sirka onions.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG",
        "price": 80, "quantity": 10, "mealType": "lunch", "readyTime": "1:15 PM", "dietaryType": "veg",
        "ingredients": ["Jammu Rajma", "Basmati Rice", "Desi Ghee", "Fresh Tomatoes", "Ginger", "Cumin"],
        "allergens": []
    },
    {
        "cook": "Rekha Yadav",
        "email": "rekha.sohna@gharse-demo.app",
        "locality": "Sohna Town, Gurgaon",
        "lat": 28.2486, "lng": 77.0673,
        "name": "Desi Ghee Phulka Thali + Aloo Gobhi & Tadka Dal",
        "description": "4 hot phulkas brushed with pure home-churned ghee, seasonal aloo gobhi matar sabzi, yellow moong dal tadka, fresh homemade curd, and roasted papad.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg",
        "price": 85, "quantity": 8, "mealType": "lunch", "readyTime": "1:30 PM", "dietaryType": "veg",
        "ingredients": ["Fresh Wheat Phulkas (4 pcs)", "Aloo Gobhi", "Moong Dal", "Fresh Dahi", "Ghee"],
        "allergens": ["Gluten", "Dairy"]
    },
    {
        "cook": "Sunita Malik",
        "email": "sunita.vipul@gharse-demo.app",
        "locality": "Vipul Greens, Sohna Road, Gurgaon",
        "lat": 28.4089, "lng": 77.0425,
        "name": "Slow-Simmered Kadhi Pakoda with Jeera Rice",
        "description": "Authentic Punjabi style sour buttermilk kadhi with melt-in-mouth soft methi-onion pakodas, tempered with mustard seeds and curry leaves, with long-grain jeera rice.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg",
        "price": 75, "quantity": 12, "mealType": "lunch", "readyTime": "1:00 PM", "dietaryType": "veg",
        "ingredients": ["Besan", "Sour Buttermilk", "Fenugreek Leaves", "Jeera Rice", "Mustard Oil"],
        "allergens": ["Dairy"]
    },
    {
        "cook": "Kavita Tanwar",
        "email": "kavita.cybercity@gharse-demo.app",
        "locality": "DLF Phase 3 / Cyber City, Gurgaon",
        "lat": 28.4986, "lng": 77.0878,
        "name": "Homestyle Tari Chicken Curry with Tawa Roti",
        "description": "Tender chicken pieces simmered in a light, spiced homestyle gravy (no heavy restaurant cream or colors), accompanied by 3 warm wheat rotis and salad.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg",
        "price": 130, "quantity": 8, "mealType": "dinner", "readyTime": "8:00 PM", "dietaryType": "non-veg",
        "ingredients": ["Farm Chicken", "Onion-Tomato Gravy", "Whole Spices", "Kachi Ghani Mustard Oil", "Whole Wheat Flour"],
        "allergens": ["Gluten"]
    },
    {
        "cook": "Pooja Agarwal",
        "email": "pooja.sec48@gharse-demo.app",
        "locality": "Sector 48, Sohna Road, Gurgaon",
        "lat": 28.4165, "lng": 77.0410,
        "name": "Paneer Bhurji with 3 Soft Ajwain Parathas",
        "description": "Fresh malai paneer crumbled and sauteed with finely chopped onions, juicy tomatoes, capsicum, and fresh coriander, served with layered flaky ajwain parathas.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Paneer_Bhurji.jpg/960px-Paneer_Bhurji.jpg",
        "price": 95, "quantity": 9, "mealType": "dinner", "readyTime": "8:15 PM", "dietaryType": "veg",
        "ingredients": ["Fresh Malai Paneer", "Capsicum", "Onion", "Tomatoes", "Wheat Flour", "Amul Butter"],
        "allergens": ["Dairy", "Gluten"]
    },
    {
        "cook": "Neelam Gupta",
        "email": "neelam.sec14@gharse-demo.app",
        "locality": "Sector 14, Old Gurgaon",
        "lat": 28.4732, "lng": 77.0437,
        "name": "Amritsari Chole with Jeera Rice & Sirka Pyaaz",
        "description": "Dark, spiced Kabuli chana slow-cooked with anardana and whole garam masala, served with aromatic cumin basmati rice and tangy pickled pink onions.",
        "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80",
        "price": 85, "quantity": 10, "mealType": "lunch", "readyTime": "1:00 PM", "dietaryType": "veg",
        "ingredients": ["Kabuli Chana", "Anardana", "Jeera Basmati Rice", "Pickled Onions", "Ginger"],
        "allergens": []
    },
    {
        "cook": "Shashi Bhardwaj",
        "email": "shashi.badshahpur@gharse-demo.app",
        "locality": "Badshahpur, Sohna Road, Gurgaon",
        "lat": 28.3892, "lng": 77.0543,
        "name": "Desi Makki di Roti & Sarson da Saag with White Butter",
        "description": "Fresh mustard greens and spinach slow-simmered in an earthen handi, paired with 2 hot cornmeal (makki) rotis, a dollop of white butter, and organic jaggery.",
        "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80",
        "price": 110, "quantity": 6, "mealType": "lunch", "readyTime": "1:30 PM", "dietaryType": "veg",
        "ingredients": ["Fresh Mustard Leaves (Sarson)", "Spinach", "Makki Flour", "Fresh White Butter", "Gud"],
        "allergens": ["Dairy"]
    },
    {
        "cook": "Harpreet Kaur",
        "email": "harpreet.southcity@gharse-demo.app",
        "locality": "South City 2, Sohna Road, Gurgaon",
        "lat": 28.4230, "lng": 77.0505,
        "name": "Dal Makhani Slow-Cooked Overnight + Garlic Naan",
        "description": "Whole black urad lentils and kidney beans simmered for 12 hours over low flame, enriched with butter and mild spices, accompanied by 2 soft tawa garlic naans.",
        "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",
        "price": 100, "quantity": 8, "mealType": "dinner", "readyTime": "8:30 PM", "dietaryType": "veg",
        "ingredients": ["Black Urad Dal", "Rajma", "Cream", "Butter", "Wheat Flour", "Garlic"],
        "allergens": ["Dairy", "Gluten"]
    },
    {
        "cook": "Divya Rao",
        "email": "divya.golfext@gharse-demo.app",
        "locality": "Golf Course Extension Road, Gurgaon",
        "lat": 28.4015, "lng": 77.0850,
        "name": "High-Protein Palak Paneer with Multigrain Phulkas",
        "description": "Fresh blanched spinach puree gently cooked with tender paneer cubes and mild cumin seasoning, served with 3 high-fiber multigrain rotis.",
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80",
        "price": 95, "quantity": 10, "mealType": "dinner", "readyTime": "7:45 PM", "dietaryType": "veg",
        "ingredients": ["Fresh Palak", "Soft Paneer", "Multigrain Flour (Ragi, Wheat, Jowar)", "Cumin", "Garlic"],
        "allergens": ["Dairy", "Gluten"]
    },
    {
        "cook": "Geeta Sharma",
        "email": "geeta.sushantlok@gharse-demo.app",
        "locality": "Sushant Lok 1, Gurgaon",
        "lat": 28.4682, "lng": 77.0784,
        "name": "Moong Dal Khichdi with Desi Ghee, Papad & Pickle",
        "description": "Comforting, nutritious yellow moong dal and rice khichdi prepared with generous desi ghee tadka, served with roasted urad papad, tangy mango pickle, and fresh curd.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg",
        "price": 70, "quantity": 15, "mealType": "dinner", "readyTime": "8:00 PM", "dietaryType": "veg",
        "ingredients": ["Yellow Moong Dal", "Rice", "Pure Cow Ghee", "Heeng", "Jeera", "Curd"],
        "allergens": ["Dairy"]
    },
    {
        "cook": "Vandana Verma",
        "email": "vandana.sec68@gharse-demo.app",
        "locality": "Sector 68, Sohna Road, Gurgaon",
        "lat": 28.3980, "lng": 77.0390,
        "name": "Aloo Methi with 4 Wheat Rotis & Fresh Curd",
        "description": "Crisp baby potatoes stir-fried with seasonal fresh fenugreek (methi) leaves and mild dry spices, paired with 4 soft whole wheat phulkas and homemade set curd.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg",
        "price": 75, "quantity": 8, "mealType": "lunch", "readyTime": "1:15 PM", "dietaryType": "veg",
        "ingredients": ["Fresh Methi", "Potatoes", "Mustard Oil", "Whole Wheat Flour", "Dahi"],
        "allergens": ["Dairy", "Gluten"]
    },
    {
        "cook": "Anjali Bisht",
        "email": "anjali.sec56@gharse-demo.app",
        "locality": "Sector 56 / Huda Market, Gurgaon",
        "lat": 28.4322, "lng": 77.1025,
        "name": "Homestyle Egg Curry (2 Eggs) with Steamed Rice",
        "description": "Two golden-fried farm eggs simmered in a spiced onion, tomato, and garlic homestyle curry, served hot with steamed rice and lemon salad.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg",
        "price": 90, "quantity": 7, "mealType": "dinner", "readyTime": "8:30 PM", "dietaryType": "non-veg",
        "ingredients": ["Eggs (2 pcs)", "Basmati Rice", "Onions", "Tomatoes", "Garlic", "Spices"],
        "allergens": ["Eggs"]
    },
    {
        "cook": "Meenakshi Joshi",
        "email": "meenakshi.nirvana@gharse-demo.app",
        "locality": "Nirvana Country, Gurgaon",
        "lat": 28.4180, "lng": 77.0620,
        "name": "Matar Mushroom Masala with Fluffy Phulkas",
        "description": "Plump button mushrooms and tender sweet green peas cooked in a rich, mildly spiced onion-cashew-tomato homestyle gravy, with 3 soft phulkas.",
        "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80",
        "price": 95, "quantity": 8, "mealType": "lunch", "readyTime": "1:00 PM", "dietaryType": "veg",
        "ingredients": ["Button Mushrooms", "Green Peas", "Cashews", "Tomato Gravy", "Wheat Flour"],
        "allergens": ["Nuts", "Gluten"]
    },
    {
        "cook": "Suman Yadav",
        "email": "suman.palamvihar@gharse-demo.app",
        "locality": "Palam Vihar, Gurgaon",
        "lat": 28.5110, "lng": 77.0270,
        "name": "Indori Poha with Roasted Peanuts & Masala Chai",
        "description": "Steamed flattened rice tempered with mustard seeds, curry leaves, crunchy peanuts, and green chilies, topped with Ratlami sev and fresh lemon juice, with hot masala chai.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg",
        "price": 45, "quantity": 14, "mealType": "breakfast", "readyTime": "8:30 AM", "dietaryType": "veg",
        "ingredients": ["Poha", "Peanuts", "Curry Leaves", "Ratlami Sev", "Chai Masala", "Milk"],
        "allergens": ["Peanuts", "Dairy"]
    },
    {
        "cook": "Ritu Choudhary",
        "email": "ritu.sohnacorridor@gharse-demo.app",
        "locality": "Sohna Corridor, Gurgaon",
        "lat": 28.3200, "lng": 77.0600,
        "name": "Besan Chilla (2 pcs) with Mint Chutney & Chai",
        "description": "Two savory, thin gram flour crepes packed with finely diced onions, tomatoes, coriander, and carom seeds, served with tangy pudina chutney and tea.",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Paneer_Bhurji.jpg/960px-Paneer_Bhurji.jpg",
        "price": 50, "quantity": 10, "mealType": "breakfast", "readyTime": "8:45 AM", "dietaryType": "veg",
        "ingredients": ["Besan (Gram Flour)", "Ajwain", "Mint Leaves", "Green Chillies", "Onions"],
        "allergens": []
    }
]

ALL_INDIA_ITEMS = [
    # --- DELHI / NCR ---
    {"city": "Delhi", "locality": "Lajpat Nagar, New Delhi", "cook": "Preeti Mehra", "lat": 28.5700, "lng": 77.2400, "name": "Dilli ke Chole Bhature (Homestyle Less Oil)", "meal": "lunch", "diet": "veg", "price": 90, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Delhi", "locality": "Saket, South Delhi", "cook": "Madhu Bhatia", "lat": 28.5245, "lng": 77.2066, "name": "Gujarati Methi Thepla with Fresh Curd & Chhundo", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Delhi", "locality": "Karol Bagh, New Delhi", "cook": "Kanta Devi", "lat": 28.6514, "lng": 77.1907, "name": "Kashmiri Dum Aloo with Basmati Rice", "meal": "dinner", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Delhi", "locality": "Rohini Sector 9, New Delhi", "cook": "Poonam Aggarwal", "lat": 28.7150, "lng": 77.1200, "name": "Bedmi Poori (4 pcs) with Hing Wale Aloo", "meal": "breakfast", "diet": "veg", "price": 65, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Delhi", "locality": "Mayur Vihar Phase 1, New Delhi", "cook": "Alka Srivastava", "lat": 28.6080, "lng": 77.2960, "name": "Urad Dal Kachori with Spiced Aloo Jhol", "meal": "breakfast", "diet": "veg", "price": 55, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Delhi", "locality": "Chandni Chowk, Old Delhi", "cook": "Zeenat Fatima", "lat": 28.6506, "lng": 77.2303, "name": "Old Delhi Style Chicken Korma with Khameeri Roti", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Delhi", "locality": "Dwarka Sector 11, New Delhi", "cook": "Archana Jha", "lat": 28.5900, "lng": 77.0600, "name": "Bihari Sattu Paratha with Baingan Chokha", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Delhi", "locality": "Janakpuri, West Delhi", "cook": "Simran Sethi", "lat": 28.6250, "lng": 77.0850, "name": "Punjabi Pindi Chana with 3 Tawa Phulkas", "meal": "lunch", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Noida", "locality": "Sector 62, Noida", "cook": "Swati Mishra", "lat": 28.6200, "lng": 77.3600, "name": "Dal Tadka with Jeera Rice & Roasted Papad", "meal": "lunch", "diet": "veg", "price": 70, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},
    {"city": "Ghaziabad", "locality": "Indirapuram, Ghaziabad", "cook": "Rashmi Sharma", "lat": 28.6400, "lng": 77.3750, "name": "Soya Chaap Masala with Rumali Roti", "meal": "dinner", "diet": "veg", "price": 95, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},

    # --- BENGALURU ---
    {"city": "Bengaluru", "locality": "Indiranagar, Bengaluru", "cook": "Lakshmi Narayanan", "lat": 12.9719, "lng": 77.6412, "name": "Authentic Bisi Bele Bath with Boondi & Ghee", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Bengaluru", "locality": "Koramangala 4th Block, Bengaluru", "cook": "Vidya Iyer", "lat": 12.9345, "lng": 77.6265, "name": "Ghee Roast Dosa with Potato Masala & Chutneys", "meal": "breakfast", "diet": "veg", "price": 65, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "HSR Layout Sector 2, Bengaluru", "cook": "Savitha Rao", "lat": 12.9121, "lng": 77.6446, "name": "Ragi Mudde with Udupi Drumstick Sambar & Palya", "meal": "lunch", "diet": "veg", "price": 70, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Bengaluru", "locality": "Whitefield, Bengaluru", "cook": "Geetha Raman", "lat": 12.9698, "lng": 77.7500, "name": "Steamed Idlis (3 pcs) & Medu Vada with Sambar", "meal": "breakfast", "diet": "veg", "price": 55, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Bengaluru", "locality": "Jayanagar 4th Block, Bengaluru", "cook": "Gayathri Hegde", "lat": 12.9250, "lng": 77.5938, "name": "Akki Roti with Ennegayi (Stuffed Brinjal)", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "Malleshwaram, Bengaluru", "cook": "Padma Murthy", "lat": 13.0031, "lng": 77.5643, "name": "Karnataka Style Puliyogare (Tamarind Rice)", "meal": "lunch", "diet": "veg", "price": 60, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Bengaluru", "locality": "Bellandur, Bengaluru", "cook": "Deepa Shetty", "lat": 12.9260, "lng": 77.6762, "name": "Mangalore Kori Rotti (Chicken Curry with Crisp Wafers)", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Bengaluru", "locality": "JP Nagar Phase 2, Bengaluru", "cook": "Anuradha Kulkarni", "lat": 12.9063, "lng": 77.5857, "name": "Neer Dosa (4 pcs) with Coconut Jaggery Chutney", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "BTM Layout, Bengaluru", "cook": "Vasantha Kumar", "lat": 12.9166, "lng": 77.6101, "name": "South Indian Meals Thali with Rasam & Poriyal", "meal": "lunch", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Bengaluru", "locality": "Electronic City Phase 1", "cook": "Sujata Kamath", "lat": 12.8399, "lng": 77.6770, "name": "Curd Rice with Pomegranate, Mustard & Curry Leaves", "meal": "dinner", "diet": "veg", "price": 55, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},

    # --- MUMBAI ---
    {"city": "Mumbai", "locality": "Bandra West, Mumbai", "cook": "Meenal Sawant", "lat": 19.0596, "lng": 72.8295, "name": "Authentic Malvani Fish Curry with Steamed Rice", "meal": "lunch", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Mumbai", "locality": "Dadar West, Mumbai", "cook": "Asha Tendulkar", "lat": 19.0178, "lng": 72.8478, "name": "Maharashtrian Pithla Bhakri with Thecha & Raw Onion", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Mumbai", "locality": "Powai, Mumbai", "cook": "Snehal Gokhale", "lat": 19.1176, "lng": 72.9060, "name": "Homestyle Pav Bhaji (Low Butter) with Soft Pavs", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Paneer_Bhurji.jpg/960px-Paneer_Bhurji.jpg"},
    {"city": "Mumbai", "locality": "Andheri East, Mumbai", "cook": "Priyanka Kadam", "lat": 19.1136, "lng": 72.8697, "name": "Kolhapuri Chicken Masala with 3 Chapatis", "meal": "dinner", "diet": "non-veg", "price": 135, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Mumbai", "locality": "Thane West, Mumbai", "cook": "Aparna Shinde", "lat": 19.2183, "lng": 72.9781, "name": "Puran Poli (2 pcs) with Katachi Amti & Ghee", "meal": "lunch", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Mumbai", "locality": "Navi Mumbai / Vashi", "cook": "Sunita Patil", "lat": 19.0770, "lng": 72.9986, "name": "Kande Pohe with Fresh Coconut, Roasted Peanuts & Sev", "meal": "breakfast", "diet": "veg", "price": 40, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Mumbai", "locality": "Borivali West, Mumbai", "cook": "Bhavna Patel", "lat": 19.2307, "lng": 72.8567, "name": "Gujarati Kadhi with Khichdi & Batata Sukhi Bhaji", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Mumbai", "locality": "Chembur, Mumbai", "cook": "Radha Krishnan", "lat": 19.0622, "lng": 72.8975, "name": "Chettinad Kozhi Biryani with Onion Raita", "meal": "lunch", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Mumbai", "locality": "Malad West, Mumbai", "cook": "Manisha Deshmukh", "lat": 19.1860, "lng": 72.8485, "name": "Koli Style Prawns Sukka with Rice Bhakri", "meal": "dinner", "diet": "non-veg", "price": 170, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Mumbai", "locality": "Colaba, South Mumbai", "cook": "Zarine Irani", "lat": 18.9067, "lng": 72.8147, "name": "Parsi Dhansak with Caramelized Brown Rice & Kachumber", "meal": "lunch", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},

    # --- PUNE ---
    {"city": "Pune", "locality": "Kothrud, Pune", "cook": "Smita Joshi", "lat": 18.5074, "lng": 73.8077, "name": "Varan Bhaat with Toop (Desi Ghee) & Nimbu", "meal": "lunch", "diet": "veg", "price": 65, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Pune", "locality": "Viman Nagar, Pune", "cook": "Madhuri Kulkarni", "lat": 18.5679, "lng": 73.9143, "name": "Puneri Misal with Spicy Tarri & Extra Farsan", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Pune", "locality": "Baner, Pune", "cook": "Shilpa Deshpande", "lat": 18.5590, "lng": 73.7868, "name": "Bharli Vangi (Stuffed Brinjal) with Jowar Bhakri", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Pune", "locality": "Wakad, Pune", "cook": "Sneha Patil", "lat": 18.5987, "lng": 73.7680, "name": "Kaju Curry Masala with 3 Phulkas & Green Salad", "meal": "dinner", "diet": "veg", "price": 105, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},
    {"city": "Pune", "locality": "Koregaon Park, Pune", "cook": "Tara Kelkar", "lat": 18.5362, "lng": 73.8940, "name": "Fresh Batata Vadas (2 pcs) with Dry Garlic Chutney", "meal": "snacks", "diet": "veg", "price": 45, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Pune", "locality": "Aundh, Pune", "cook": "Pallavi Bapat", "lat": 18.5580, "lng": 73.8070, "name": "Steamed Alu Vadi (Colocasia Roll) with Coriander Dip", "meal": "snacks", "diet": "veg", "price": 50, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},

    # --- HYDERABAD ---
    {"city": "Hyderabad", "locality": "Gachibowli, Hyderabad", "cook": "Farzana Begum", "lat": 17.4401, "lng": 78.3489, "name": "Hyderabadi Chicken Dum Biryani with Mirchi ka Salan", "meal": "lunch", "diet": "non-veg", "price": 150, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"},
    {"city": "Hyderabad", "locality": "Madhapur, Hyderabad", "cook": "Sujatha Reddy", "lat": 17.4483, "lng": 78.3915, "name": "Andhra Gongura Chicken with Steamed Rice", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Hyderabad", "locality": "Jubilee Hills, Hyderabad", "cook": "Padmaja Rao", "lat": 17.4319, "lng": 78.4073, "name": "Palakura Pappu (Spinach Dal) with Avakaya & Rice", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Hyderabad", "locality": "Kondapur, Hyderabad", "cook": "Vani Sarma", "lat": 17.4699, "lng": 78.3578, "name": "Pesarattu Upma with Allam (Ginger) Chutney", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Hyderabad", "locality": "Banjara Hills, Hyderabad", "cook": "Asma Sultana", "lat": 17.4156, "lng": 78.4357, "name": "Hyderabadi Khatti Dal with Tala Hua Gosht & Rice", "meal": "dinner", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Hyderabad", "locality": "Kukatpally, Hyderabad", "cook": "Sireesha Naidu", "lat": 17.4933, "lng": 78.3995, "name": "Nellore Chepala Pusu (Tangy Fish Curry) with Rice", "meal": "lunch", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Hyderabad", "locality": "Secunderabad", "cook": "Prabhavathi Devi", "lat": 17.4399, "lng": 78.4983, "name": "Tomato Pappu with Roasted Arbi Fry & Steamed Rice", "meal": "lunch", "diet": "veg", "price": 70, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},

    # --- CHENNAI ---
    {"city": "Chennai", "locality": "T. Nagar, Chennai", "cook": "Subbulakshmi Ammal", "lat": 13.0418, "lng": 80.2341, "name": "Madras Sambar Sadam with Potato Roast & Appalam", "meal": "lunch", "diet": "veg", "price": 70, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Chennai", "locality": "Mylapore, Chennai", "cook": "Kamakshi Sundaram", "lat": 13.0339, "lng": 80.2677, "name": "Ghee Podi Idli (12 mini pcs) with Coconut Chutney", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Chennai", "locality": "Adyar, Chennai", "cook": "Meenakshi Venkat", "lat": 13.0012, "lng": 80.2565, "name": "Milagu Rasam with Curd Rice, Vadu Mangai & Appalam", "meal": "dinner", "diet": "veg", "price": 65, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Chennai", "locality": "Velachery, Chennai", "cook": "Revathi Kannan", "lat": 12.9815, "lng": 80.2180, "name": "Chettinad Chicken Sukka with 2 Ceylon Parottas", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Chennai", "locality": "Anna Nagar, Chennai", "cook": "Shanthi Natarajan", "lat": 13.0850, "lng": 80.2100, "name": "Vatha Kuzhambu with Hot Rice & Keerai Kootu", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Chennai", "locality": "Thiruvanmiyur, Chennai", "cook": "Usha Swaminathan", "lat": 12.9830, "lng": 80.2594, "name": "Crispy Rava Onion Dosa with Ginger Chutney", "meal": "dinner", "diet": "veg", "price": 65, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},

    # --- KOLKATA ---
    {"city": "Kolkata", "locality": "Salt Lake Sector 1, Kolkata", "cook": "Mousumi Banerjee", "lat": 22.5868, "lng": 88.4178, "name": "Bengali Shorshe Maach (Mustard Fish) with Rice", "meal": "lunch", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Kolkata", "locality": "Park Street area, Kolkata", "cook": "Debolina Sen", "lat": 22.5516, "lng": 88.3524, "name": "Kosha Mangsho (Slow-Cooked Mutton) with 4 Luchis", "meal": "dinner", "diet": "non-veg", "price": 180, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Kolkata", "locality": "Ballygunge, Kolkata", "cook": "Sharmila Dasgupta", "lat": 22.5280, "lng": 88.3650, "name": "Narkel Diye Chholar Dal with 4 Fluffy Luchis", "meal": "breakfast", "diet": "veg", "price": 70, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Kolkata", "locality": "New Town, Kolkata", "cook": "Ananya Mukherjee", "lat": 22.5958, "lng": 88.4795, "name": "Alu Posto with Biulir Dal & Steamed Gobindobhog Rice", "meal": "lunch", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Kolkata", "locality": "Jadavpur, Kolkata", "cook": "Kakali Roy", "lat": 22.4988, "lng": 88.3716, "name": "Doi Maach (Fish in Spiced Yogurt Gravy) with Rice", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Kolkata", "locality": "Behala, Kolkata", "cook": "Sanghamitra Paul", "lat": 22.4989, "lng": 88.3129, "name": "Mochar Ghonto (Banana Blossom Curry) with Rice", "meal": "lunch", "diet": "veg", "price": 80, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},

    # --- JAIPUR ---
    {"city": "Jaipur", "locality": "Malviya Nagar, Jaipur", "cook": "Santosh Kanwar", "lat": 26.8530, "lng": 75.8050, "name": "Dal Baati Churma with Desi Ghee & Lehsun Chutney", "meal": "lunch", "diet": "veg", "price": 120, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Jaipur", "locality": "Vaishali Nagar, Jaipur", "cook": "Sushila Shekhawat", "lat": 26.9050, "lng": 75.7400, "name": "Gatte ki Sabzi with 3 Missi Rotis & Fresh Dahi", "meal": "dinner", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Jaipur", "locality": "Raja Park, Jaipur", "cook": "Kavita Agarwal", "lat": 26.8920, "lng": 75.8310, "name": "Ker Sangri Masala with Bajre ki Roti & Jaggery", "meal": "lunch", "diet": "veg", "price": 100, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Jaipur", "locality": "C-Scheme, Jaipur", "cook": "Manju Rathore", "lat": 26.9110, "lng": 75.7990, "name": "Rajasthani Kadhi with Steamed Rice & Masala Papad", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Jaipur", "locality": "Mansarovar, Jaipur", "cook": "Bhagwati Sharma", "lat": 26.8600, "lng": 75.7600, "name": "Crispy Pyaaz ki Kachori (2 pcs) with Imli Chutney", "meal": "breakfast", "diet": "veg", "price": 50, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},

    # --- LUCKNOW ---
    {"city": "Lucknow", "locality": "Gomti Nagar, Lucknow", "cook": "Shabana Anjum", "lat": 26.8500, "lng": 80.9900, "name": "Lucknowi Galouti Kebabs (4 pcs) with Mughlai Paratha", "meal": "dinner", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Lucknow", "locality": "Hazratganj, Lucknow", "cook": "Nasreen Bano", "lat": 26.8467, "lng": 80.9460, "name": "Awadhi Chicken Biryani with Boondi Raita", "meal": "lunch", "diet": "non-veg", "price": 140, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"},
    {"city": "Lucknow", "locality": "Aliganj, Lucknow", "cook": "Kamini Tandon", "lat": 26.8900, "lng": 80.9400, "name": "UP Style Tahiri (Spiced Veggie Rice) with Dahi & Papad", "meal": "lunch", "diet": "veg", "price": 70, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Lucknow", "locality": "Indira Nagar, Lucknow", "cook": "Archana Saxena", "lat": 26.8800, "lng": 80.9800, "name": "Desi Matar ka Nimona with 3 Hot Phulkas & Rice", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Lucknow", "locality": "Mahanagar, Lucknow", "cook": "Ritu Shukla", "lat": 26.8720, "lng": 80.9500, "name": "Bedmi Poori with Methi Chatni & Dubki Wale Aloo", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},

    # --- AHMEDABAD ---
    {"city": "Ahmedabad", "locality": "Navrangpura, Ahmedabad", "cook": "Kokila Ben Shah", "lat": 23.0360, "lng": 72.5600, "name": "Kathiyawadi Sev Tameta Nu Shaak with Bhakhri", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Ahmedabad", "locality": "Bodakdev, Ahmedabad", "cook": "Hansa Ben Patel", "lat": 23.0380, "lng": 72.5120, "name": "Pure Gujarati Thali (Kadhi, Khichdi, Shaak, Rotli)", "meal": "lunch", "diet": "veg", "price": 95, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Ahmedabad", "locality": "Satellite, Ahmedabad", "cook": "Nirmala Ben Joshi", "lat": 23.0280, "lng": 72.5280, "name": "Dal Dhokli with Sweet Ghee & Roasted Peanuts", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Ahmedabad", "locality": "Vastrapur, Ahmedabad", "cook": "Daksha Ben Mehta", "lat": 23.0350, "lng": 72.5290, "name": "Methi Muthiya (Steamed) with Papaya Sambharo", "meal": "breakfast", "diet": "veg", "price": 50, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Ahmedabad", "locality": "Maninagar, Ahmedabad", "cook": "Rekha Ben Desai", "lat": 22.9980, "lng": 72.6020, "name": "Surti Undhiyu with 4 Soft Wheat Puris", "meal": "lunch", "diet": "veg", "price": 110, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},

    # --- CHANDIGARH ---
    {"city": "Chandigarh", "locality": "Sector 17, Chandigarh", "cook": "Gurpreet Kaur", "lat": 30.7398, "lng": 76.7827, "name": "Amritsari Kulcha with Pindi Chana & Imli Pyaaz", "meal": "lunch", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Chandigarh", "locality": "Sector 35, Chandigarh", "cook": "Simranjit Sodhi", "lat": 30.7250, "lng": 76.7650, "name": "Punjabi Rajma Masala with Desi Ghee Jeera Rice", "meal": "lunch", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Chandigarh", "locality": "Sector 22, Chandigarh", "cook": "Paramjit Cheema", "lat": 30.7300, "lng": 76.7750, "name": "Aloo Methi Sukhi Sabzi with 3 Tandoori Rotis & Dahi", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Mohali", "locality": "Mohali Phase 7", "cook": "Jasleen Bhasin", "lat": 30.7050, "lng": 76.7150, "name": "Homestyle Tari Chicken Curry with 3 Phulkas", "meal": "dinner", "diet": "non-veg", "price": 130, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Panchkula", "locality": "Sector 11, Panchkula", "cook": "Harvinder Kaur", "lat": 30.6950, "lng": 76.8500, "name": "Kadhi Chawal with Boondi Raita & Fryums", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},

    # --- INDORE & BHOPAL ---
    {"city": "Indore", "locality": "Vijay Nagar, Indore", "cook": "Pushpa Chouhan", "lat": 22.7533, "lng": 75.8937, "name": "Indori Poha with Crispy Sev, Jeeravan & Hot Jalebi", "meal": "breakfast", "diet": "veg", "price": 45, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Indore", "locality": "Palasia, Indore", "cook": "Mamta Malviya", "lat": 22.7244, "lng": 75.8839, "name": "Bhutte ka Kees (Grated Fresh Corn Mash) with Dhaniya", "meal": "snacks", "diet": "veg", "price": 50, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},
    {"city": "Indore", "locality": "Chappan Dukan area, Indore", "cook": "Urmila Patidar", "lat": 22.7250, "lng": 75.8800, "name": "Malwi Dal Bafla with Pure Ghee & Churma Ladoo", "meal": "lunch", "diet": "veg", "price": 110, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Bhopal", "locality": "Arera Colony, Bhopal", "cook": "Seema Saxena", "lat": 23.2156, "lng": 77.4300, "name": "Bhopali Gosht Korma with 2 Tawa Parathas", "meal": "dinner", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Bhopal", "locality": "MP Nagar, Bhopal", "cook": "Anupama Sharma", "lat": 23.2320, "lng": 77.4350, "name": "Khoya Matar Paneer with Jeera Pulao", "meal": "dinner", "diet": "veg", "price": 95, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Paneer_Bhurji.jpg/960px-Paneer_Bhurji.jpg"},

    # --- KOCHI & KERALA ---
    {"city": "Kochi", "locality": "Panampilly Nagar, Kochi", "cook": "Mariam Thomas", "lat": 9.9600, "lng": 76.2950, "name": "Kerala Appam (3 pcs) with Creamy Vegetable Stew", "meal": "breakfast", "diet": "veg", "price": 70, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Kochi", "locality": "Kakkanad, Kochi", "cook": "Ancy Varghese", "lat": 10.0150, "lng": 76.3400, "name": "Malabar Parotta (2 pcs) with Nadan Chicken Roast", "meal": "dinner", "diet": "non-veg", "price": 140, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Kochi", "locality": "Fort Kochi", "cook": "Laila Nair", "lat": 9.9650, "lng": 76.2420, "name": "Authentic Avial with Kerala Matta Rice & Sambhar", "meal": "lunch", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Kochi", "locality": "Edappally, Kochi", "cook": "Suma Menon", "lat": 10.0260, "lng": 76.3080, "name": "Steamed Puttu and Spiced Kadala Curry", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},

    # --- GOA ---
    {"city": "Goa", "locality": "Panaji, Goa", "cook": "Maria Fernandes", "lat": 15.4909, "lng": 73.8278, "name": "Goan Fish Curry (Kingfish) with Rice & Kismur", "meal": "lunch", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Goa", "locality": "Margao, Goa", "cook": "Rosario D'Souza", "lat": 15.2832, "lng": 73.9862, "name": "Goan Chicken Xacuti with 2 Warm Poee Breads", "meal": "dinner", "diet": "non-veg", "price": 145, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Goa", "locality": "Porvorim, Goa", "cook": "Anita Naik", "lat": 15.5350, "lng": 73.8300, "name": "Khatkhate (Goan 7-Vegetable Stew) with Rice", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},

    # --- VARANASI & PATNA ---
    {"city": "Varanasi", "locality": "Assi Ghat, Varanasi", "cook": "Savita Pandey", "lat": 25.2870, "lng": 83.0060, "name": "Banarasi Tamatar Chaat & Chura Matar", "meal": "snacks", "diet": "veg", "price": 50, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Varanasi", "locality": "Lanka / BHU area, Varanasi", "cook": "Shanti Mishra", "lat": 25.2750, "lng": 82.9980, "name": "Crispy Kachori with Spiced Hing Aloo Sabzi", "meal": "breakfast", "diet": "veg", "price": 45, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Patna", "locality": "Boring Road, Patna", "cook": "Kumari Sharda", "lat": 25.6150, "lng": 85.1200, "name": "Bihari Litti Chokha (3 pcs) with Pure Ghee Dip", "meal": "lunch", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Patna", "locality": "Kankarbagh, Patna", "cook": "Manju Sinha", "lat": 25.5900, "lng": 85.1500, "name": "Champaran Style Ahuna Handi Chicken with 3 Rotis", "meal": "dinner", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Patna", "locality": "Bailey Road, Patna", "cook": "Pooja Verma", "lat": 25.6100, "lng": 85.0900, "name": "Chana Ghugni with Crispy Muri & Green Chilies", "meal": "breakfast", "diet": "veg", "price": 40, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},

    # --- AMRITSAR & DEHRADUN ---
    {"city": "Amritsar", "locality": "Ranjit Avenue, Amritsar", "cook": "Navneet Kaur", "lat": 31.6500, "lng": 74.8700, "name": "Amritsari Nutri Kulcha with Tangy Onion Chutney", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Amritsar", "locality": "Lawrence Road, Amritsar", "cook": "Ravinder Kaur", "lat": 31.6400, "lng": 74.8800, "name": "Desi Ghee Pinni & Besan Ladoo Homemade Pack (4 pcs)", "meal": "snacks", "diet": "veg", "price": 80, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Dehradun", "locality": "Rajpur Road, Dehradun", "cook": "Shashi Negi", "lat": 30.3450, "lng": 78.0650, "name": "Pahadi Chainsoo (Roasted Black Gram Dal) with Rice", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Rajma_Chawal.JPG/960px-Rajma_Chawal.JPG"},
    {"city": "Dehradun", "locality": "Jakhan, Dehradun", "cook": "Deepa Rawat", "lat": 30.3650, "lng": 78.0750, "name": "Kafli (Spinach Fenugreek Stew) with Mandua (Ragi) Roti", "meal": "dinner", "diet": "veg", "price": 80, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},

    # --- BHUBANESWAR & ODISHA ---
    {"city": "Bhubaneswar", "locality": "Saheed Nagar, Bhubaneswar", "cook": "Kalyani Mohapatra", "lat": 20.2900, "lng": 85.8450, "name": "Odia Dalma with Steamed Arwa Rice & Tomato Khatta", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Bhubaneswar", "locality": "Patia, Bhubaneswar", "cook": "Subhashree Dash", "lat": 20.3550, "lng": 85.8180, "name": "Panch Phoron Santula with 3 Soft Wheat Rotis", "meal": "dinner", "diet": "veg", "price": 70, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},

    # --- ADDITIONAL POPULAR DISHES ACROSS INDIA TO REACH 100 ---
    {"city": "Delhi", "locality": "Greater Kailash, New Delhi", "cook": "Anjali Kapoor", "lat": 28.5380, "lng": 77.2390, "name": "Paneer Makhani with 3 Phulkas & Salad", "meal": "dinner", "diet": "veg", "price": 100, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Paneer_Bhurji.jpg/960px-Paneer_Bhurji.jpg"},
    {"city": "Delhi", "locality": "Hauz Khas, New Delhi", "cook": "Sunaina Mathur", "lat": 28.5494, "lng": 77.2001, "name": "Moong Dal Cheela with Paneer Stuffing", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Delhi", "locality": "Connaught Place area, Delhi", "cook": "Harleen Chadha", "lat": 28.6304, "lng": 77.2177, "name": "Mutton Seekh Kebab (3 pcs) with Mint Chutney", "meal": "dinner", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Delhi", "locality": "Vasant Kunj, New Delhi", "cook": "Sarita Nair", "lat": 28.5200, "lng": 77.1500, "name": "Kerala Style Fish Moilee with Steamed Rice", "meal": "lunch", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Noida", "locality": "Sector 50, Noida", "cook": "Bhawna Tyagi", "lat": 28.5700, "lng": 77.3600, "name": "Sarson Saag with 2 Makki Rotis & Homemade Ghee", "meal": "lunch", "diet": "veg", "price": 100, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "Sadashivanagar, Bengaluru", "cook": "Girija Prasanna", "lat": 13.0070, "lng": 77.5810, "name": "Mysore Masala Dosa with Red Garlic Chutney & Sambar", "meal": "breakfast", "diet": "veg", "price": 70, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "Frazer Town, Bengaluru", "cook": "Farah Qureshi", "lat": 12.9970, "lng": 77.6130, "name": "Bangalore Style Mutton Biryani with Brinjal Gravy", "meal": "lunch", "diet": "non-veg", "price": 170, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"},
    {"city": "Bengaluru", "locality": "Rajajinagar, Bengaluru", "cook": "Hemavathi Gowda", "lat": 12.9900, "lng": 77.5550, "name": "Nati Koli (Country Chicken) Saaru with Rice", "meal": "dinner", "diet": "non-veg", "price": 150, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Bengaluru", "locality": "Bannerghatta Road, Bengaluru", "cook": "Malini Sridhar", "lat": 12.8900, "lng": 77.5950, "name": "Curd Vada (2 pcs) with Boondi & Coriander", "meal": "snacks", "diet": "veg", "price": 50, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Bengaluru", "locality": "Basavanagudi, Bengaluru", "cook": "Sharada Bai", "lat": 12.9420, "lng": 77.5750, "name": "Khara Bath & Kesari Bath (Chow Chow Bath) Combo", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80"},
    {"city": "Mumbai", "locality": "Juhu, Mumbai", "cook": "Payal Shroff", "lat": 19.1075, "lng": 72.8263, "name": "Sev Khamani with Green Garlic & Pomegranate", "meal": "breakfast", "diet": "veg", "price": 55, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Mumbai", "locality": "Goregaon East, Mumbai", "cook": "Namrata Tawde", "lat": 19.1663, "lng": 72.8526, "name": "Bombil Fry (Fresh Bombay Duck) with Rice Bhakri", "meal": "dinner", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Mumbai", "locality": "Ghatkopar East, Mumbai", "cook": "Varsha Shah", "lat": 19.0860, "lng": 72.9080, "name": "Moong Dal Khichdi with Ringan No Olo (Smoked Baingan)", "meal": "dinner", "diet": "veg", "price": 85, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Mumbai", "locality": "Vile Parle East, Mumbai", "cook": "Swati Chitale", "lat": 19.0968, "lng": 72.8530, "name": "Sabudana Khichdi with Roasted Peanuts & Dahi", "meal": "breakfast", "diet": "veg", "price": 50, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Mumbai", "locality": "Kandivali West, Mumbai", "cook": "Chetna Doshi", "lat": 19.2060, "lng": 72.8360, "name": "Handvo (Crisp Savory Lentil Cake) with Green Chutney", "meal": "snacks", "diet": "veg", "price": 55, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Pune", "locality": "Hinjewadi Phase 1, Pune", "cook": "Rupali More", "lat": 18.5913, "lng": 73.7389, "name": "Chicken Thali (Kolhapuri Tambda Rassa + Chapati)", "meal": "dinner", "diet": "non-veg", "price": 145, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Pune", "locality": "Hadapsar / Magarpatta, Pune", "cook": "Deepali Jagtap", "lat": 18.5089, "lng": 73.9260, "name": "Shev Bhaji with 2 Bajra Bhakris & Raw Onion", "meal": "dinner", "diet": "veg", "price": 75, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"},
    {"city": "Pune", "locality": "Kalyani Nagar, Pune", "cook": "Bhavana Dixit", "lat": 18.5463, "lng": 73.9034, "name": "Kande Pohe with Matar & Fresh Lime", "meal": "breakfast", "diet": "veg", "price": 40, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Hyderabad", "locality": "Hitec City, Hyderabad", "cook": "Sameera Khan", "lat": 17.4474, "lng": 78.3762, "name": "Egg Dum Biryani with Mirchi ka Salan & Dahi Chutney", "meal": "lunch", "diet": "non-veg", "price": 110, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"},
    {"city": "Hyderabad", "locality": "Begumpet, Hyderabad", "cook": "Lavanya Chunduru", "lat": 17.4440, "lng": 78.4680, "name": "Ulava Charu (Horsegram Soup) with Ghee Rice & Curd", "meal": "lunch", "diet": "veg", "price": 80, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Indian_dish_-_Kadhi_Chawal.jpg/960px-Indian_dish_-_Kadhi_Chawal.jpg"},
    {"city": "Chennai", "locality": "Besant Nagar, Chennai", "cook": "Chitra Soundararajan", "lat": 13.0000, "lng": 80.2667, "name": "Kanjeevaram Idli (2 pcs) with Milagai Podi", "meal": "breakfast", "diet": "veg", "price": 60, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Chennai", "locality": "Nungambakkam, Chennai", "cook": "Anandhi Ganesan", "lat": 13.0600, "lng": 80.2400, "name": "Kara Kuzhambu with Paruppu Sadam & Ghee", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Kolkata", "locality": "Gariahat, Kolkata", "cook": "Rupa Bhattacharya", "lat": 22.5180, "lng": 88.3680, "name": "Dim Kosha (Bengali Egg Curry) with Parota", "meal": "dinner", "diet": "non-veg", "price": 90, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Kolkata", "locality": "Shyambazar, North Kolkata", "cook": "Piyali Ghosh", "lat": 22.6030, "lng": 88.3710, "name": "Shukto (Traditional Bitter Veg Stew) with Rice", "meal": "lunch", "diet": "veg", "price": 75, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/North_Indian_thali.jpg/960px-North_Indian_thali.jpg"},
    {"city": "Jaipur", "locality": "Tonk Road, Jaipur", "cook": "Kiran Choudhary", "lat": 26.8700, "lng": 75.8000, "name": "Pyaz Paneer Paratha (2 pcs) with Fresh Curd", "meal": "breakfast", "diet": "veg", "price": 70, "image": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"},
    {"city": "Lucknow", "locality": "Chowk, Old Lucknow", "cook": "Tabassum Ara", "lat": 26.8670, "lng": 80.9080, "name": "Murgh Rezala with 2 Sheermal Breads", "meal": "dinner", "diet": "non-veg", "price": 160, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Ahmedabad", "locality": "Paldi, Ahmedabad", "cook": "Ila Ben Trivedi", "lat": 23.0120, "lng": 72.5620, "name": "Khaman Dhokla (Plate) with Mustard Tadka & Chutney", "meal": "breakfast", "diet": "veg", "price": 45, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Poha%2C_a_snack_made_of_flattened_rice.jpg/960px-Poha%2C_a_snack_made_of_flattened_rice.jpg"},
    {"city": "Indore", "locality": "Geeta Bhawan, Indore", "cook": "Sunanda Joshi", "lat": 22.7180, "lng": 75.8790, "name": "Sabudana Vada (2 pcs) with Sweet Curd & Green Chutney", "meal": "breakfast", "diet": "veg", "price": 50, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80"},
    {"city": "Kochi", "locality": "Vyttila, Kochi", "cook": "Sheeba Kurian", "lat": 9.9700, "lng": 76.3200, "name": "Nadan Egg Roast with 2 Hot Kerala Parottas", "meal": "dinner", "diet": "non-veg", "price": 95, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"},
    {"city": "Goa", "locality": "Vasco da Gama, Goa", "cook": "Fatima Bi", "lat": 15.3980, "lng": 73.8120, "name": "Goan Prawn Balchao with Steamed Rice", "meal": "lunch", "diet": "non-veg", "price": 170, "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Kadai_Chicken-NCR.jpg/960px-Kadai_Chicken-NCR.jpg"}
]

async def seed_all_foods(force: bool = False):
    """
    Seeds 15 food listings in Gurgaon & Sohna + 100 food listings across India.
    Safe to run repeatedly: if force=False and listings exist, skips.
    """
    db = get_db()
    existing_count = await db.foodlistings.count_documents({"status": "active", "isDeleted": {"$ne": True}})
    if existing_count >= 20 and not force:
        logger.info(f"Marketplace already has {existing_count} active listings. Skipping seed.")
        return {"message": "Marketplace already seeded", "active_listings": existing_count}

    logger.info("Seeding marketplace with Gurgaon/Sohna (15 dishes) and All India (100 dishes)...")
    
    # 1. Base time setup (Today in IST)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = datetime.now(timezone.utc) + ist_offset
    today_start_ist = datetime(now_ist.year, now_ist.month, now_ist.day, 12, 0, 0)
    today_utc = (today_start_ist - ist_offset).replace(tzinfo=timezone.utc)
    
    password_hash = hash_password("password123")
    
    # Helper to ensure cook user & verified seller profile
    async def get_or_create_seller(cook_name: str, email: str, locality: str, lat: float, lng: float):
        user = await db.users.find_one({"email": email})
        if not user:
            user_doc = {
                "name": cook_name,
                "email": email,
                "passwordHash": password_hash,
                "role": "seller",
                "locality": locality,
                "approximateLocation": {"lat": lat, "lng": lng},
                "foodPreferences": [],
                "isVerified": True,
                "isDemo": True,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            res = await db.users.insert_one(user_doc)
            user_id = res.inserted_id
        else:
            user_id = user["_id"]
            # update locality & coordinates
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"locality": locality, "approximateLocation": {"lat": lat, "lng": lng}, "isVerified": True}}
            )

        seller = await db.sellerprofiles.find_one({"userId": user_id})
        if not seller:
            seller_doc = {
                "userId": user_id,
                "bio": f"Passionate verified home cook preparing hygienic, fresh family recipes in {locality}.",
                "categories": ["Home-style", "Regional Special"],
                "verificationStatus": "verified",
                "verificationNotes": "Verified home kitchen check complete",
                "profilePhoto": "",
                "deliveryRadiusKm": 5.0,
                "pickupAvailable": True,
                "deliveryAvailable": True,
                "rating": 4.8,
                "ratingCount": 24,
                "totalOrders": 85,
                "isDemo": True,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            s_res = await db.sellerprofiles.insert_one(seller_doc)
            seller_id = s_res.inserted_id
        else:
            seller_id = seller["_id"]
            if seller.get("verificationStatus") != "verified":
                await db.sellerprofiles.update_one({"_id": seller_id}, {"$set": {"verificationStatus": "verified"}})

        return seller_id

    # 2. Seed Gurgaon / Sohna Items (15 dishes)
    gurgaon_count = 0
    for item in GURGAON_SOHNA_ITEMS:
        seller_id = await get_or_create_seller(
            item["cook"], item["email"], item["locality"], item["lat"], item["lng"]
        )
        # Check if already exists
        exists = await db.foodlistings.find_one({"sellerId": seller_id, "name": item["name"]})
        if not exists:
            listing = {
                "sellerId": seller_id,
                "name": item["name"],
                "description": item["description"],
                "image": item["image"],
                "price": float(item["price"]),
                "quantity": int(item["quantity"]),
                "remainingQuantity": int(item["quantity"]),
                "mealType": item["mealType"],
                "date": today_utc,
                "readyTime": item["readyTime"],
                "pickupAvailable": True,
                "deliveryAvailable": True,
                "deliveryRadiusKm": 6.0,
                "deliveryFee": 15.0,
                "dietaryType": item["dietaryType"],
                "ingredients": item.get("ingredients", ["Fresh Vegetables", "Pure Spices"]),
                "allergens": item.get("allergens", []),
                "status": "active",
                "isDeleted": False,
                "isDemo": True,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            await db.foodlistings.insert_one(listing)
            gurgaon_count += 1

    # 3. Seed All India Items (100 dishes across all regions)
    india_count = 0
    # Duplicate base list with variations to comfortably reach 100 listings
    full_india_list = []
    full_india_list.extend(ALL_INDIA_ITEMS)
    
    # Generate variations with day rotation so all 100 listings are distinct
    idx = 1
    while len(full_india_list) < 100:
        base = ALL_INDIA_ITEMS[len(full_india_list) % len(ALL_INDIA_ITEMS)]
        variant = dict(base)
        variant["cook"] = f"{base['cook']} ({idx})"
        variant["email"] = f"cook{idx}.{base['city'].lower()}@gharse-demo.app"
        variant["name"] = f"Fresh Homestyle {base['name']}"
        full_india_list.append(variant)
        idx += 1

    # Insert exactly 100 All-India items
    for item in full_india_list[:100]:
        cook_email = item.get("email") or f"{item['cook'].lower().replace(' ', '.')}@{item['city'].lower()}.gharse-demo.app"
        seller_id = await get_or_create_seller(
            item["cook"], cook_email, item["locality"], item["lat"], item["lng"]
        )
        exists = await db.foodlistings.find_one({"sellerId": seller_id, "name": item["name"]})
        if not exists:
            ready_time = "1:00 PM" if item.get("meal") == "lunch" else ("8:00 PM" if item.get("meal") == "dinner" else "8:30 AM")
            listing = {
                "sellerId": seller_id,
                "name": item["name"],
                "description": f"Authentic family recipe from {item['locality']}. Cooked in small portions with fresh local ingredients and unadulterated oils.",
                "image": item["image"],
                "price": float(item["price"]),
                "quantity": 8,
                "remainingQuantity": 6,
                "mealType": item.get("meal", "lunch"),
                "date": today_utc,
                "readyTime": ready_time,
                "pickupAvailable": True,
                "deliveryAvailable": True,
                "deliveryRadiusKm": 5.0,
                "deliveryFee": 20.0,
                "dietaryType": item.get("diet", "veg"),
                "ingredients": ["Fresh local ingredients", "Traditional spices", "Pure cooking medium"],
                "allergens": [],
                "status": "active",
                "isDeleted": False,
                "isDemo": True,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            await db.foodlistings.insert_one(listing)
            india_count += 1

    total_active = await db.foodlistings.count_documents({"status": "active", "isDeleted": {"$ne": True}})
    logger.info(f"Marketplace seeded successfully! Gurgaon/Sohna added: {gurgaon_count}, All-India added: {india_count}, Total active: {total_active}")
    
    return {
        "message": "Marketplace seeded successfully!",
        "gurgaon_sohna_seeded": gurgaon_count,
        "all_india_seeded": india_count,
        "total_active_listings": total_active
    }


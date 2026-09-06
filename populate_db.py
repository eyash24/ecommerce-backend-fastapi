import asyncio
from datetime import UTC, datetime, timedelta
import random
import httpx
from sqlalchemy import delete, select, update

import models
from database import AsyncSessionLocal, engine

from main import app

USERS = [
    {
        "username": "AppMaintainer",
        "email": "TestEmailAPP@test.com",
        "password": "TestPassword1!",
        "image_url": "https://images.pexels.com/photos/19453607/pexels-photo-19453607.jpeg",
    },
    {
        "username": "DefaultDude",
        "email": "TestEmail2@test.com",
        "password": "TestPassword2!",
        "image_url": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg",
    },
    {
        "username": "WillowTheCat",
        "email": "TestEmail3@test.com",
        "password": "TestPassword3!",
        "image_url": "https://images.pexels.com/photos/104827/cat-pet-animal-domestic-104827.jpeg",
    },
    {
        "username": "FarmDogs",
        "email": "TestEmail4@test.com",
        "password": "TestPassword4!",
        "image_url": "https://images.pexels.com/photos/1805164/pexels-photo-1805164.jpeg",
    },
    {
        "username": "PoppyTheCoder",
        "email": "TestEmail5@test.com",
        "password": "TestPassword5!",
        "image_url": "https://images.pexels.com/photos/1681010/pexels-photo-1681010.jpeg",
    },
    {
        "username": "GoodBoyBronx",
        "email": "TestEmail6@test.com",
        "password": "TestPassword6!",
        "image_url": "https://images.pexels.com/photos/1805164/pexels-photo-1805164.jpeg",
    },
]

PRODUCTS = [
    {
        "product": {
            "name": "Wireless Headphones",
            "description": "Over-ear wireless headphones with active noise cancellation, deep bass, and up to 30 hours of battery life.",
            "price": 7999.00,
            "image_url": "https://picsum.photos/seed/headphones/600/600",
            "category": "electronics",
            "quantity": 24,
        },
        "reviews": [
            {
                "title": "Excellent sound quality",
                "rating": 5.0,
                "comment": "The audio is clear with strong bass, and the noise cancellation works surprisingly well.",
            },
            {
                "title": "Very comfortable",
                "rating": 4.5,
                "comment": "Comfortable even after several hours. Battery life is also very impressive.",
            },
            {
                "title": "Perfect for travel",
                "rating": 5.0,
                "comment": "Used them during a long flight and they blocked most of the cabin noise.",
            },
            {
                "title": "Good but slightly bulky",
                "rating": 4.0,
                "comment": "Sound quality is excellent, although the headphones are a little large for carrying around.",
            },
            {
                "title": "Worth the price",
                "rating": 4.5,
                "comment": "Great build quality, good connectivity, and impressive battery performance.",
            },
        ],
    },

    {
        "product": {
            "name": "Smart Fitness Watch",
            "description": "Smartwatch with heart-rate monitoring, sleep tracking, GPS, activity tracking, and notification support.",
            "price": 5499.00,
            "image_url": "https://picsum.photos/seed/smartwatch/600/600",
            "category": "electronics",
            "quantity": 18,
        },
        "reviews": [
            {
                "title": "Great fitness companion",
                "rating": 4.5,
                "comment": "Step tracking and heart-rate monitoring work well and the battery lasts several days.",
            },
            {
                "title": "Good smartwatch",
                "rating": 4.0,
                "comment": "The display is bright and notifications work reliably with my phone.",
            },
            {
                "title": "Useful tracking features",
                "rating": 4.5,
                "comment": "Sleep tracking and workout tracking are very helpful for keeping track of daily activity.",
            },
            {
                "title": "Nice design",
                "rating": 4.0,
                "comment": "Looks premium and is comfortable enough to wear throughout the day.",
            },
        ],
    },

    {
        "product": {
            "name": "Bluetooth Speaker",
            "description": "Portable waterproof Bluetooth speaker with stereo sound, strong bass, and up to 12 hours of battery life.",
            "price": 2999.00,
            "image_url": "https://picsum.photos/seed/speaker/600/600",
            "category": "electronics",
            "quantity": 32,
        },
        "reviews": [
            {
                "title": "Amazing sound",
                "rating": 5.0,
                "comment": "Very loud for such a compact speaker and the bass is much better than expected.",
            },
            {
                "title": "Perfect for small parties",
                "rating": 4.5,
                "comment": "Easy to connect and produces enough volume for a medium-sized room.",
            },
            {
                "title": "Good battery life",
                "rating": 4.0,
                "comment": "Battery easily lasts through an evening and Bluetooth connectivity is stable.",
            },
            {
                "title": "Great portable speaker",
                "rating": 4.5,
                "comment": "Compact, durable, and convenient to carry while travelling.",
            },
        ],
    },

    {
        "product": {
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard with tactile switches, programmable lighting, anti-ghosting, and durable keycaps.",
            "price": 4299.00,
            "image_url": "https://picsum.photos/seed/keyboard/600/600",
            "category": "electronics",
            "quantity": 0,
        },
        "reviews": [
            {
                "title": "Fantastic keyboard",
                "rating": 5.0,
                "comment": "The switches feel responsive and typing on this keyboard is extremely satisfying.",
            },
            {
                "title": "Love the RGB",
                "rating": 4.5,
                "comment": "Lighting looks great and the keyboard feels solid during gaming.",
            },
            {
                "title": "Solid build",
                "rating": 4.5,
                "comment": "Feels much heavier and more durable than cheaper mechanical keyboards.",
            },
            {
                "title": "Excellent for gaming",
                "rating": 5.0,
                "comment": "Fast key response and no noticeable input issues during games.",
            },
            {
                "title": "Very good overall",
                "rating": 4.0,
                "comment": "Keyboard itself is excellent, although the customization software could be better.",
            },
        ],
    },

    # =========================================================
    # CLOTHING
    # =========================================================

    {
        "product": {
            "name": "Classic Cotton T-Shirt",
            "description": "Soft cotton crew-neck t-shirt designed for comfortable everyday casual wear.",
            "price": 799.00,
            "image_url": "https://picsum.photos/seed/tshirt/600/600",
            "category": "clothing",
            "quantity": 40,
        },
        "reviews": [
            {
                "title": "Very comfortable",
                "rating": 4.5,
                "comment": "Soft and breathable material that feels comfortable throughout the day.",
            },
            {
                "title": "Good quality",
                "rating": 4.0,
                "comment": "The fabric and stitching are both good considering the price.",
            },
            {
                "title": "Nice fit",
                "rating": 4.5,
                "comment": "Fits exactly as expected and looks good with jeans.",
            },
            {
                "title": "Great value",
                "rating": 5.0,
                "comment": "Simple, comfortable, and good quality for everyday wear.",
            },
        ],
    },

    {
        "product": {
            "name": "Slim Fit Denim Jeans",
            "description": "Stretch denim jeans with a modern slim fit, durable stitching, and comfortable everyday styling.",
            "price": 1999.00,
            "image_url": "https://picsum.photos/seed/jeans/600/600",
            "category": "clothing",
            "quantity": 26,
        },
        "reviews": [
            {
                "title": "Good fit",
                "rating": 4.0,
                "comment": "The stretch fabric makes these jeans comfortable while still maintaining a slim fit.",
            },
            {
                "title": "Excellent denim",
                "rating": 4.5,
                "comment": "The denim feels durable and the fit is exactly what I wanted.",
            },
            {
                "title": "Comfortable jeans",
                "rating": 4.0,
                "comment": "Comfortable enough for all-day wear and pairs nicely with casual shirts.",
            },
            {
                "title": "Looks great",
                "rating": 4.5,
                "comment": "Nice color and the slim cut looks modern without being too tight.",
            },
        ],
    },

    {
        "product": {
            "name": "Lightweight Hoodie",
            "description": "Soft fleece hoodie with an adjustable drawstring hood, front pocket, and relaxed fit.",
            "price": 1499.00,
            "image_url": "https://picsum.photos/seed/hoodie/600/600",
            "category": "clothing",
            "quantity": 21,
        },
        "reviews": [
            {
                "title": "Super comfortable",
                "rating": 5.0,
                "comment": "The inside is soft and comfortable without making the hoodie feel too heavy.",
            },
            {
                "title": "Good hoodie",
                "rating": 4.0,
                "comment": "Nice material and fits according to the listed size.",
            },
            {
                "title": "Warm and lightweight",
                "rating": 4.5,
                "comment": "Perfect for slightly cold weather and easy to layer with other clothing.",
            },
            {
                "title": "Good purchase",
                "rating": 4.5,
                "comment": "The color, stitching, and fabric all feel good for this price.",
            },
        ],
    },

    {
        "product": {
            "name": "Casual Linen Shirt",
            "description": "Breathable linen-blend shirt with a relaxed fit, ideal for casual outings and warm weather.",
            "price": 1799.00,
            "image_url": "https://picsum.photos/seed/linenshirt/600/600",
            "category": "clothing",
            "quantity": 0,
        },
        "reviews": [
            {
                "title": "Great summer shirt",
                "rating": 4.5,
                "comment": "Lightweight and breathable, making it comfortable even during hot weather.",
            },
            {
                "title": "Looks stylish",
                "rating": 4.0,
                "comment": "The relaxed fit and fabric give it a clean casual appearance.",
            },
            {
                "title": "Excellent quality",
                "rating": 4.5,
                "comment": "Fabric feels better than expected and the stitching is neat.",
            },
            {
                "title": "Nice casual shirt",
                "rating": 4.0,
                "comment": "Comfortable shirt that works well for casual outings.",
            },
        ],
    },

    # =========================================================
    # HOME & KITCHEN
    # =========================================================

    {
        "product": {
            "name": "Stainless Steel Cookware Set",
            "description": "Seven-piece stainless steel cookware set with durable handles and even heat distribution.",
            "price": 5499.00,
            "image_url": "https://picsum.photos/seed/cookware/600/600",
            "category": "home & kitchen",
            "quantity": 19,
        },
        "reviews": [
            {
                "title": "Excellent cookware",
                "rating": 5.0,
                "comment": "The pans feel sturdy and distribute heat evenly while cooking.",
            },
            {
                "title": "Great quality",
                "rating": 4.5,
                "comment": "Stainless steel feels premium and the entire set seems durable.",
            },
            {
                "title": "Good kitchen set",
                "rating": 4.0,
                "comment": "Contains most of the cookware needed for everyday cooking.",
            },
            {
                "title": "Easy to clean",
                "rating": 4.5,
                "comment": "Food residue washes off easily and the cookware still looks new.",
            },
        ],
    },

    {
        "product": {
            "name": "Digital Kitchen Scale",
            "description": "Compact digital kitchen scale with precise measurements, LCD display, and tare functionality.",
            "price": 899.00,
            "image_url": "https://picsum.photos/seed/kitchenscale/600/600",
            "category": "home & kitchen",
            "quantity": 35,
        },
        "reviews": [
            {
                "title": "Very accurate",
                "rating": 5.0,
                "comment": "Measurements are consistent and the display is easy to read.",
            },
            {
                "title": "Useful kitchen tool",
                "rating": 4.5,
                "comment": "Small enough to store easily and useful for baking and meal preparation.",
            },
            {
                "title": "Great for baking",
                "rating": 4.5,
                "comment": "Makes measuring flour and other ingredients much more convenient.",
            },
            {
                "title": "Simple and reliable",
                "rating": 4.0,
                "comment": "Nothing complicated about it and measurements seem accurate.",
            },
        ],
    },

    {
        "product": {
            "name": "Ceramic Dinner Set",
            "description": "Sixteen-piece ceramic dinner set including plates, bowls, mugs, and side plates.",
            "price": 3299.00,
            "image_url": "https://picsum.photos/seed/dinnerset/600/600",
            "category": "home & kitchen",
            "quantity": 22,
        },
        "reviews": [
            {
                "title": "Beautiful dinner set",
                "rating": 5.0,
                "comment": "The design looks elegant and makes the dining table look much better.",
            },
            {
                "title": "Good ceramic quality",
                "rating": 4.0,
                "comment": "The pieces feel sturdy and the finish is smooth.",
            },
            {
                "title": "Nice everyday set",
                "rating": 4.5,
                "comment": "Good collection of pieces for a small family.",
            },
            {
                "title": "Looks premium",
                "rating": 4.5,
                "comment": "Design and finish look more expensive than the actual price.",
            },
        ],
    },

    {
        "product": {
            "name": "Electric Coffee Maker",
            "description": "Programmable coffee maker with reusable filter, large water reservoir, and automatic keep-warm function.",
            "price": 2799.00,
            "image_url": "https://picsum.photos/seed/coffeemaker/600/600",
            "category": "home & kitchen",
            "quantity": 0,
        },
        "reviews": [
            {
                "title": "Easy to use",
                "rating": 4.0,
                "comment": "Straightforward controls and makes good coffee without much effort.",
            },
            {
                "title": "Great morning coffee",
                "rating": 4.5,
                "comment": "The programmable timer is useful for having coffee ready in the morning.",
            },
            {
                "title": "Good coffee maker",
                "rating": 4.0,
                "comment": "Works reliably and cleanup is fairly simple.",
            },
            {
                "title": "Very convenient",
                "rating": 4.5,
                "comment": "Large enough for several cups and the reusable filter is a nice addition.",
            },
        ],
    },

    # =========================================================
    # BOOKS
    # =========================================================

    {
        "product": {
            "name": "The Art of Programming",
            "description": "A beginner-friendly introduction to programming concepts, algorithms, problem solving, and software development.",
            "price": 699.00,
            "image_url": "https://picsum.photos/seed/programmingbook/600/600",
            "category": "books",
            "quantity": 28,
        },
        "reviews": [
            {
                "title": "Excellent beginner book",
                "rating": 5.0,
                "comment": "Programming concepts are explained clearly and examples are easy to understand.",
            },
            {
                "title": "Very informative",
                "rating": 4.5,
                "comment": "A useful starting point for anyone beginning their programming journey.",
            },
            {
                "title": "Good explanations",
                "rating": 4.5,
                "comment": "The chapters are organized well and concepts build naturally on one another.",
            },
            {
                "title": "Highly recommended",
                "rating": 5.0,
                "comment": "Provides a strong foundation before moving into more advanced programming topics.",
            },
        ],
    },

    {
        "product": {
            "name": "Atomic Habits",
            "description": "A practical guide to developing good habits, breaking bad habits, and improving through small daily changes.",
            "price": 599.00,
            "image_url": "https://picsum.photos/seed/atomichabits/600/600",
            "category": "books",
            "quantity": 45,
        },
        "reviews": [
            {
                "title": "Very practical",
                "rating": 5.0,
                "comment": "The ideas are easy to understand and can be applied immediately.",
            },
            {
                "title": "Great book",
                "rating": 5.0,
                "comment": "A useful approach to improving daily routines through small consistent changes.",
            },
            {
                "title": "Easy to read",
                "rating": 4.5,
                "comment": "The examples and stories make the concepts enjoyable and memorable.",
            },
            {
                "title": "Highly recommended",
                "rating": 5.0,
                "comment": "One of the most practical books I have read about building habits.",
            },
            {
                "title": "Useful ideas",
                "rating": 4.5,
                "comment": "Some sections repeat similar ideas, but the overall message is very valuable.",
            },
        ],
    },

    {
        "product": {
            "name": "Clean Code",
            "description": "A software development book focused on writing readable, maintainable, testable, and professional-quality code.",
            "price": 899.00,
            "image_url": "https://picsum.photos/seed/cleancode/600/600",
            "category": "books",
            "quantity": 17,
        },
        "reviews": [
            {
                "title": "Essential for developers",
                "rating": 5.0,
                "comment": "Contains many valuable principles for writing maintainable and understandable software.",
            },
            {
                "title": "Very useful",
                "rating": 4.5,
                "comment": "Some examples are dated, but the underlying software principles are still valuable.",
            },
            {
                "title": "Excellent resource",
                "rating": 5.0,
                "comment": "Changed the way I think about naming, functions, classes, and code structure.",
            },
            {
                "title": "Good technical book",
                "rating": 4.0,
                "comment": "Worth reading once you already understand the basics of programming.",
            },
        ],
    },

    {
        "product": {
            "name": "The Psychology of Money",
            "description": "A collection of lessons exploring how behavior, emotions, and personal experiences influence financial decisions.",
            "price": 549.00,
            "image_url": "https://picsum.photos/seed/moneybook/600/600",
            "category": "books",
            "quantity": 0,
        },
        "reviews": [
            {
                "title": "Great perspective",
                "rating": 5.0,
                "comment": "Makes you think differently about saving, spending, investing, and personal wealth.",
            },
            {
                "title": "Easy to understand",
                "rating": 4.5,
                "comment": "Financial ideas are explained through stories rather than complicated formulas.",
            },
            {
                "title": "Very insightful",
                "rating": 4.5,
                "comment": "The chapters are short but contain many useful lessons about financial behavior.",
            },
            {
                "title": "Enjoyable read",
                "rating": 5.0,
                "comment": "An interesting combination of finance, psychology, and real-world examples.",
            },
        ],
    },

    # =========================================================
    # SPORTS & FITNESS
    # =========================================================

    {
        "product": {
            "name": "Adjustable Dumbbell Set",
            "description": "Space-saving adjustable dumbbells with multiple weight settings for strength training and home workouts.",
            "price": 4999.00,
            "image_url": "https://picsum.photos/seed/dumbbells/600/600",
            "category": "sports & fitness",
            "quantity": 20,
        },
        "reviews": [
            {
                "title": "Perfect for home workouts",
                "rating": 5.0,
                "comment": "Takes up much less space than owning several pairs of dumbbells.",
            },
            {
                "title": "Excellent build",
                "rating": 4.5,
                "comment": "The dumbbells feel sturdy and switching between weights is simple.",
            },
            {
                "title": "Great equipment",
                "rating": 4.5,
                "comment": "Works well for a wide range of strength exercises at home.",
            },
            {
                "title": "Very convenient",
                "rating": 5.0,
                "comment": "Changing weights takes only a few seconds and saves a lot of room.",
            },
        ],
    },

    {
        "product": {
            "name": "Non-Slip Yoga Mat",
            "description": "Cushioned exercise mat with a non-slip surface for yoga, stretching, mobility exercises, and workouts.",
            "price": 899.00,
            "image_url": "https://picsum.photos/seed/yogamat/600/600",
            "category": "sports & fitness",
            "quantity": 38,
        },
        "reviews": [
            {
                "title": "Great yoga mat",
                "rating": 5.0,
                "comment": "Provides good grip and enough cushioning for daily yoga sessions.",
            },
            {
                "title": "Comfortable mat",
                "rating": 4.5,
                "comment": "The thickness provides good support without making balance difficult.",
            },
            {
                "title": "Does not slip",
                "rating": 4.5,
                "comment": "The surface stays in place well even during more active workouts.",
            },
            {
                "title": "Good value",
                "rating": 4.0,
                "comment": "A simple and comfortable mat for stretching and home workouts.",
            },
        ],
    },

    {
        "product": {
            "name": "Resistance Band Set",
            "description": "Five resistance bands with different resistance levels for strength training, mobility, and rehabilitation exercises.",
            "price": 699.00,
            "image_url": "https://picsum.photos/seed/resistancebands/600/600",
            "category": "sports & fitness",
            "quantity": 31,
        },
        "reviews": [
            {
                "title": "Great workout equipment",
                "rating": 4.5,
                "comment": "Having several resistance levels makes this set useful for many different exercises.",
            },
            {
                "title": "Good bands",
                "rating": 4.0,
                "comment": "Compact and easy to carry while still providing useful resistance.",
            },
            {
                "title": "Useful set",
                "rating": 4.5,
                "comment": "The bands feel durable and work well for strength and mobility exercises.",
            },
            {
                "title": "Good for beginners",
                "rating": 4.0,
                "comment": "An inexpensive and convenient way to start resistance training.",
            },
        ],
    },

    {
        "product": {
            "name": "Running Shoes",
            "description": "Lightweight running shoes with breathable mesh, responsive cushioning, and comfortable everyday support.",
            "price": 3499.00,
            "image_url": "https://picsum.photos/seed/runningshoes/600/600",
            "category": "sports & fitness",
            "quantity": 0,
        },
        "reviews": [
            {
                "title": "Very comfortable",
                "rating": 5.0,
                "comment": "The cushioning is comfortable even during longer runs.",
            },
            {
                "title": "Great running shoes",
                "rating": 4.5,
                "comment": "Lightweight design with good support and breathable material.",
            },
            {
                "title": "Good shoes",
                "rating": 4.0,
                "comment": "Comfortable enough for both running and everyday walking.",
            },
            {
                "title": "Excellent for jogging",
                "rating": 5.0,
                "comment": "Used them regularly for jogging and the cushioning still feels great.",
            },
            {
                "title": "Nice cushioning",
                "rating": 4.5,
                "comment": "Good impact absorption and the shoes feel light while running.",
            },
            {
                "title": "Worth the price",
                "rating": 4.5,
                "comment": "Comfortable, lightweight, and suitable for regular running sessions.",
            },
        ],
    },
]

async def clear_existing_data() -> None:
    async with AsyncSessionLocal() as db:
        await db.execute(delete(models.User))
        await db.execute(delete(models.Product))
        await db.execute(delete(models.Review))
        await db.commit()

    print('cleared existing data')

async def populate() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url='http://localhost'
    ) as client:

        await clear_existing_data()

        users: list[dict] = []

        print(f'\nCreating {len(USERS)} users ....')
        for user_data in USERS:
            response = await client.post(
                '/api/users',
                json={
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'image_url': user_data['image_url']
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f'    Created: {user['username']}')

            response = await client.post(
                '/api/users/token',
                data = {
                    'username': user_data['email'],
                    'password': user_data['password'],
                }
            )
            response.raise_for_status()
            token=response.json()['access_token']

            users.append(
                {'id': user['id'], 'username': user['username'], 'token': token},
            )

        print(f'\n Creating {len(PRODUCTS)+1} product...')
        print(users[0])

        for i, product_info in enumerate(reversed(PRODUCTS)):
            user = users[ i % len(users)]
            response = await client.post(
                '/api/products',
                json = {
                    "name" : product_info['product']["name"],
                    "description" : product_info['product']["description"],
                    "price" : product_info['product']["price"],
                    "image_url" : product_info['product']["image_url"],
                    "category" : product_info['product']["category"],
                    "quantity" : product_info['product']['quantity']
                },
                headers={'Authorization': f'Bearer {user['token']}'},
            )
            response.raise_for_status()
            product_id = response.json()['id']
            title = product_info['product']['name']
            print(
                f'  Created: {title[:50]}...'
                if len(title) > 50
                else f'  Created: {title}'
            )

            for j, review_info in enumerate(reversed(product_info['reviews'])):
                user_rev = users[(i+j) % len(users)]
                response_rev = await client.post(
                    '/api/reviews',
                    json = {
                        "title" : review_info['title'],
                        "rating" : review_info['rating'],
                        "comment" : review_info['comment'],
                        "product_id" : product_id,
                    },
                    headers={'Authorization': f'Bearer {user_rev['token']}'},
                )

                response_rev.raise_for_status()
                title_rev = review_info['title']
                print(
                    f'  Created: {title_rev[:50]}...'
                    if len(title_rev) > 50
                    else f'  Created: {title_rev}'
                )

            print(f'\n{len(product_info['reviews'])} reviews created')

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(PRODUCTS) + 1} products")


if __name__ == '__main__':
    asyncio.run(populate())
import shopify
import os




token = ""
shop = ""



api_session = shopify.Session(shop, "2022-04", token)
shopify.ShopifyResource.activate_session(api_session)

def get_data(object_name):
    all_data = []
    attribute=getattr(shopify, object_name)
    data=attribute.find(since_id=0, limit=250)
    for d in data:
        all_data.append(d)
    while data.has_next_page():
        data=data.next_page()
        for d in data:
            all_data.append(d)
    return all_data


products = get_data("Product")
with open("products.txt", "w") as f:
    for p in products:
        print(f"{p.id}\t{p.title}")
        f.write(f"{p.id}\t{p.title}\n")

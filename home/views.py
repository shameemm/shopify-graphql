from django.contrib import messages
from django.shortcuts import render, redirect
import shopify
from django.http import HttpResponse, JsonResponse
import requests, json
from django.conf import settings
from shopify_app.decorators import shop_login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def cre_product(var):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN
    query = """
    mutation createProductMetafields($input: ProductInput!) { 
        productCreate(input: $input) { 
            product { 
                id 
                metafields(first: 3) { 
                    edges { 
                        node { 
                            id 
                            namespace 
                            key 
                            value 
                        } 
                    } 
                } 
            } 
            userErrors { 
                message 
                field 
            } 
        } 
    }
    """
    payload = {
        "query": query,
        "variables": var
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token
    }
    response = requests.post(shop_url, headers=headers, data=json.dumps(payload))
    return response

def upd_product(variable):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN

    query = """
    mutation UpdateProduct($input: ProductInput!) {
        productUpdate(input: $input) {
            product {
                id
                title
                vendor
                productType
            }
            userErrors {
                field
                message
            }
        }
    }
    """
    
    payload = {
    "query": query,
    "variables": {
        "input": variable
    }
    }

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }

    response = requests.post(shop_url, json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Update Response:", response_data)
        return response
    else:
        print("Error:", response.status_code, response.text)
        return response
    
def get_product_data(product_id=None):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN
    if product_id:
        query = f"""
        query {{
            node(id: "gid://shopify/Product/{product_id}") {{
                id
                ... on Product {{
                    title
                    productType
                    vendor
                }}
            }}
        }}
        """

        headers = {
            "X-Shopify-Access-Token":access_token,
            "Content-Type": "application/json"
        }
        
        response = requests.post(shop_url, json={'query': query}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']['node']:
                return data['data']['node']
            else:
                raise ValueError("Product not found or error in query")
        else:
            raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
    else:
        query = """
            query {
                products(first: 100) {
                    edges {
                        node {
                            id
                            title
                            handle
                        }
                    }
                }
            }
            """

        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }
        response = requests.post(shop_url,json={'query':query}, headers=headers)
        return response.json()['data']['products']['edges']

@shop_login_required
def index(request):
    products = shopify.Product.find(limit=10, order="created_at DESC")

    orders = shopify.Order.find()
    return render(request, 'home/index.html', {'products': products, 'orders': orders})
    
@shop_login_required
def create_product(request):
    if request.method == "POST":
        # new_product = shopify.Product()
        # new_product.title = request.POST.get('title')
        # new_product.product_type = request.POST.get('product_type')
        # new_product.vendor = request.POST.get('vendor')

        # success = new_product.save() 
        # if success:
        #     messages.success(request, "product created")
        #     return redirect('/create')
        # else:
        #     messages.error(request, "something went wrong")
        #     return redirect('/create')
        title = request.POST.get('title')
        vendor = request.POST.get('vendor')
        product_type = request.POST.get('product_type')

        variables = {
            "input": {
                "title": title,
                "vendor": vendor,
                "productType": product_type
            }
        }

        response = cre_product(variables)
        return redirect('/')
    else:
        return render(request, 'create_product.html')
@shop_login_required    
def update_product(request, id):
    if request.method == "POST":
        title = request.POST.get('title')
        vendor = request.POST.get('vendor')
        product_type = request.POST.get('product_type')
        product_id = f"gid://shopify/Product/{id}"
        product_input = {
            "id": product_id ,
            "title": title, 
            "vendor": vendor,
            "productType": product_type
            }
        upd_product(product_input)
        return redirect('/')
    else:
        product = get_product_data(id)
        product_id = product['id'].split('/')[-1]
        return render(request, 'update_product.html', {'product': product,'product_id':product_id})
        

@shop_login_required
def delete_product(request, id):
    product = shopify.Product.find(id)
    if product:
        product.destroy()
        return redirect('/')
    else:
        return HttpResponse("something wrong")
    
@shop_login_required    
def create_collection(request):
    if request.method == 'POST':
        shop_url = settings.SHOP_URL
        access_token = settings.APP_ACCESSTOKEN
        title = request.POST.get('title')
        products = request.POST.getlist('products')
        variables = {
            "input": {
                "title": title,
                "products":products,
            }
        }
        query = """
        mutation createCollectionMetafields($input: CollectionInput!) {
            collectionCreate(input: $input) {
                    collection {
                        id
                        metafields(first: 3) {
                            edges {
                                node {
                                    id
                                    namespace
                                    key
                                    value
                                }
                            }
                    }
                }
                userErrors {
                    message
                    field
                }
            }
        }"""

        payload = {
        "query": query,
        "variables": variables
        }

        headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token
        }
        response = requests.post(shop_url, headers=headers, data=json.dumps(payload))
        print(response.json())
        return redirect("/")
    else:
        # breakpoint()
        products = get_product_data()
        return render(request, 'create_collection.html',{'products':products})

class CreateProduct(APIView):
    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        vendor = request.data.get('vendor')
        product_type = request.data.get('product_type')
        try:
            variables = {
                "input": {
                    "title": title,
                    "vendor": vendor,
                    "productType": product_type
                }
            }

            response = cre_product(variables)
            print(response.json())
            return Response(response.json(),status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class UpdateProduct(APIView):

    def put(self,request, *args, **kwargs):
        title = request.data.get('title')
        vendor = request.data.get('vendor')
        id = kwargs.get('id')
        product_type = request.data.get('product_type')
        try:
            product_id = f"gid://shopify/Product/{id}"
            product_input = {
                "id": product_id ,
                "title": title, 
                "vendor": vendor,
                "productType": product_type
            }
            response = upd_product(product_input)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(response.content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

def create_draft_orders(request):
    if request.method == "POST":
        shop_url = settings.SHOP_URL
        access_token = settings.APP_ACCESSTOKEN
        email = request.POST.get('email')
        variant_id = request.POST.get("variant_id")
        quantity = request.POST.get("quantity")

        mutation = """
             mutation draftOrderCreate($input: DraftOrderInput!) {
                draftOrderCreate(input: $input) {
                    draftOrder {
                        id
                    }
                }
            }
        """

        variables = {
            "input": {
                "note": "Test draft order",
                "email": email,
                "taxExempt": True,
                "tags": [
                "foo",
                "bar"
                ],
                "shippingLine": {
                "title": "Custom Shipping",
                "price": 4.55
                },
                "useCustomerDefaultAddress":True,
                "appliedDiscount": {
                "description": "damaged",
                "value": 5,
                "amount": 5,
                "valueType": "FIXED_AMOUNT",
                "title": "Custom"
                },
                "lineItems": [
                {
                    "variantId": variant_id,
                    "quantity": int(quantity)
                },
                ],
                
            }
        }

        payload = {
        "query": mutation,
        "variables": variables
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': access_token
        }
        response = requests.post(shop_url, headers=headers, data=json.dumps(payload))

        print(response.json())
        return JsonResponse(response.json())
    else:
        return render(request, 'create_draft_order.html')
    

#-------------------------------------#
#    SUBSCRIPTIONS (SELLING PLAN)     #
#-------------------------------------#


def create_sellng_plan(request):
    # if request.method == 'POST':
        shop_url = settings.SHOP_URL
        access_token = settings.APP_ACCESSTOKEN

        mutation = f"""
          mutation {{
              sellingPlanGroupCreate(
                input: {{
                  name: "Subscribe and save or full sleeve"
                  merchantCode: "subscribe-and-save"
                  options: ["Delivery every"]
                  position: 1
                  sellingPlansToCreate: [
                    {{
                      name: "Delivered every week save 5%"
                      options: "1 week(s)"
                      position: 1
                      category: SUBSCRIPTION
                      billingPolicy: {{
                        recurring: {{
                          interval: WEEK,
                          intervalCount: 1
                          anchors: {{ type: WEEKDAY, day: 1 }}
                        }}
                      }}
                      deliveryPolicy: {{
                        recurring: {{
                          interval: WEEK,
                          intervalCount: 1
                          anchors: {{ type: WEEKDAY, day: 1 }}
                          preAnchorBehavior: ASAP
                          cutoff: 0
                          intent: FULFILLMENT_BEGIN
                        }}
                      }}
                      pricingPolicies: [
                        {{
                          fixed: {{
                            adjustmentType: PERCENTAGE
                            adjustmentValue: {{ percentage: 15.0 }}
                          }}
                        }}
                      ]
                    }}
                  ]
                }}
                resources: {{ productIds: [], productVariantIds: ["gid://shopify/ProductVariant/41352582889549"] }}
              ) {{
                sellingPlanGroup {{
                  id
                }}
                userErrors {{
                  field
                  message
                }}
              }}
            }}
        """
        
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': access_token
        }
        
        payload = {
            "query": mutation
        }
        
        response = requests.post(shop_url, json=payload, headers=headers)
        print(response.json())
        return JsonResponse(response.json())

def list_selling_plans(request):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN
    query = """
    query {
        sellingPlanGroups(first: 10) {
            edges {
                node {
                    id
                    name
                    options
                    position
                }
            }
        }
    }
    """
    headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
    }
    response = requests.post(shop_url,json={'query':query}, headers=headers)
    return JsonResponse(response.json())

def selling_plan_remove_product(request):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN

    mutation = mutation = """
        mutation sellingPlanGroupRemoveProducts($id: ID!, $productIds: [ID!]!) {
            sellingPlanGroupRemoveProducts(id: $id, productIds: $productIds) {
                removedProductIds
                userErrors {
                    field
                    message
                }
            }
        }
    """

    variables = {
        "id": "gid://shopify/SellingPlanGroup/3614244941",
        "productIds": [
            "gid://shopify/Product/7351031070797"
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token
    }

    payload = {
        "query": mutation,
        "variables": variables
    }

    response = requests.post(shop_url, json=payload, headers=headers)
    print(response.json())
    return JsonResponse(response.json()) 

def selling_plan_group_data(request):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN
    query = """
        query sellingPlanGroups {
            sellingPlanGroup(id: "gid://shopify/SellingPlanGroup/3614244941") {
                id,
                name,
                merchantCode,
                appId,
                description,
                options,
                position,
                createdAt,
                sellingPlans(first: 1) {
                    edges {
                        node {
                                id
                            }
                    }
                }
                productVariants(first: 1) {
                    edges {
                            node {
                                id
                        }
                    }
                }
                products(first: 1) {
                    edges {
                            node {
                                id
                        }
                    }
                }
            }
        }

    """
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }
    response = requests.post(shop_url,json={'query':query}, headers=headers)
    return JsonResponse(response.json())

def remove_variant_from_selling_plan(request):
    shop_url = settings.SHOP_URL
    access_token = settings.APP_ACCESSTOKEN
    query = """
        mutation sellingPlanGroupRemoveProductVariants($id: ID!, $productVariantIds: [ID!]!) {
            sellingPlanGroupRemoveProductVariants(id: $id, productVariantIds: $productVariantIds) {
                removedProductVariantIds
                userErrors {
                    field
                    message
                }
            }
        }
    """

    variables = {
        "id": "gid://shopify/SellingPlanGroup/3614244941",
        "productVariantIds": [
            "gid://shopify/ProductVariant/41352582889549"
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token
    }

    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(shop_url, json=payload, headers=headers)
    print(response.json())
    return JsonResponse(response.json()) 
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import requests

# Create your views here.
def create_cart(request,id):
    variant_id = id
    shop_url = settings.STOREFRONT_URL
    access_token = settings.STOREFRONT_ACCESSTOKEN

    mutation = f"""
    mutation {{
      cartCreate(
        input: {{
          lines: [
            {{
              quantity: 1
              merchandiseId: "gid://shopify/ProductVariant/{variant_id}"
            }}
          ],
          buyerIdentity: {{
            email: "example@example.com",
            countryCode: CA,
            deliveryAddressPreferences: {{
              oneTimeUse: false,
              deliveryAddress: {{
                address1: "150 Elgin Street",
                address2: "8th Floor",
                city: "Ottawa",
                province: "Ontario",
                country: "CA",
                zip: "K2P 1L4"
              }}
            }},
            preferences: {{
              delivery: {{
                deliveryMethod: PICK_UP
              }}
            }}
          }},
          attributes: {{
            key: "cart_attribute",
            value: "This is a cart attribute"
          }}
        }}
      ) {{
        cart {{
          id
          createdAt
          updatedAt
          lines(first: 10) {{
            edges {{
              node {{
                id
                merchandise {{
                  ... on ProductVariant {{
                    id
                  }}
                }}
              }}
            }}
          }}
          buyerIdentity {{
            deliveryAddressPreferences {{
              __typename
            }}
            preferences {{
              delivery {{
                deliveryMethod
              }}
            }}
          }}
          attributes {{
            key
            value
          }}
          cost {{
            totalAmount {{
              amount
              currencyCode
            }}
            subtotalAmount {{
              amount
              currencyCode
            }}
            totalTaxAmount {{
              amount
              currencyCode
            }}
            totalDutyAmount {{
              amount
              currencyCode
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": access_token
    }
    
    payload = {
        "query": mutation
    }
    
    response = requests.post(shop_url, json=payload, headers=headers)
    print(response.json())
    return JsonResponse(response.json())

def update_cart(request):
    if request.method == 'POST':
        shop_url = settings.STOREFRONT_URL
        access_token = settings.STOREFRONT_ACCESSTOKEN
        cart_id = request.POST.get('cart_id')
        line_id = request.POST.get('line_id')
        quantity = request.POST.get('quantity')

        mutation = f"""
        mutation {{
          cartLinesUpdate(
              cartId: "{cart_id}"
              lines: {{
                id: "{line_id}"
                quantity: {quantity}
              }}
          ) {{
              cart {{
              id
              lines(first: 100) {{
                  edges {{
                  node {{
                      id
                      quantity
                      merchandise {{
                      ... on ProductVariant {{
                          id
                      }}
                      }}
                  }}
                  }}
              }}
              cost {{
                  totalAmount {{
                    amount
                    currencyCode
                  }}
                  subtotalAmount {{
                    amount
                    currencyCode
                  }}
                  totalTaxAmount {{
                    amount
                    currencyCode
                  }}
                  totalDutyAmount {{
                    amount
                    currencyCode
                  }}
              }}
              }}
          }}
        }}
        """
        
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": access_token,
        }
        
        payload = {
            "query": mutation
        }
        
        response = requests.post(shop_url, json=payload, headers=headers)
        print(response.json())
        return JsonResponse(response.json())
    else:
        return render(request, 'cart_updation_form.html')
    
def customer_accesss_token_create(request):
    if request.method == "POST":
        shop_url = settings.STOREFRONT_URL
        access_token = settings.STOREFRONT_ACCESSTOKEN
        email = request.POST.get('email')
        password = request.POST.get('password')

        mutation = f"""
        mutation customerAccessTokenCreate {{
          customerAccessTokenCreate(input: {{email: "{email}", password: "{password}"}}) {{
            customerAccessToken {{
              accessToken
            }}
            customerUserErrors {{
              message
            }}
          }}
        }}        
        """
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": access_token,
        }
        
        payload = {
            "query": mutation
        }
        response = requests.post(shop_url, json=payload, headers=headers)
        print(response.json())
        return JsonResponse(response.json())

    else:
        return render(request, 'customer_login.html')


def create_cart_with_selling_plan(request):
    shop_url = settings.STOREFRONT_URL
    access_token = settings.STOREFRONT_ACCESSTOKEN
    mutation = """
      mutation cartCreate($input: CartInput) {
        cartCreate(input: $input) {
          cart {
            id
          }
          userErrors {
            field
            message
          }
        }
      }
    """

    variables = {
      "input": {
        "attributes": [
          {
            "key": "<your-key>",
            "value": "<your-value>"
          }
        ],
        "buyerIdentity": {
            "customerAccessToken": "34be541eb9420fe99c06c1c66f89d0bc"
        },
        "discountCodes": [
          "<your-discountCodes>"
        ],
        "giftCardCodes": [
          "<your-giftCardCodes>"
        ],
        "lines": [
          {
            "attributes": [
              {
                "key": "<your-key>",
                "value": "<your-value>"
              }
            ],
            "merchandiseId": "gid://shopify/ProductVariant/41352582889549",
            "quantity": 1,
            "sellingPlanId": "gid://shopify/SellingPlan/5445681229"
          }
        ],
        "metafields": [
        ],
        "note": "<your-note>"
      }
    }

    headers = {
          'Content-Type': 'application/json',
          'X-Shopify-Storefront-Access-Token': access_token
      }

    payload = {
        "query": mutation,
        "variables": variables
    }

    response = requests.post(shop_url, json=payload, headers=headers)
    print(response.json())
    return JsonResponse(response.json()) 

def cart_data(request):
    shop_url = settings.STOREFRONT_URL
    access_token = settings.STOREFRONT_ACCESSTOKEN
    query = """
    query {
      cart(
        id: "gid://shopify/Cart/Z2NwLWFzaWEtc291dGhlYXN0MTowMUpDSjBDNTdLNFhCUDU1OFpUQTZNSkJQUA?key=bc98f8df3b457ff08ed402bb9d74c93d"
      ) {
    id
    createdAt
    updatedAt
    lines(first: 10) {
      edges {
        node {
          id
          quantity
          merchandise {
            ... on ProductVariant {
              id
            }
          }
          attributes {
            key
            value
          }
        }
      }
    }
    attributes {
      key
      value
    }
    cost {
      totalAmount {
        amount
        currencyCode
      }
      subtotalAmount {
        amount
        currencyCode
      }
      totalTaxAmount {
        amount
        currencyCode
      }
      totalDutyAmount {
        amount
        currencyCode
      }
    }
    buyerIdentity {
      email
      phone
      customer {
        id
      }
      countryCode
      deliveryAddressPreferences {
        ... on MailingAddress {
          address1
          address2
          city
          provinceCode
          countryCodeV2
          zip
        }
      }
      preferences {
        delivery {
          deliveryMethod
        }
      }
    }
  }
}
    """
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": access_token,
    }
    payload = {
        "query": query
    }
    response = requests.post(shop_url, json=payload, headers=headers)
    print(response.json())
    return JsonResponse(response.json())  
from django.contrib import messages
from django.shortcuts import render, redirect
import csv
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
import requests
from .models import PostOffice , ScannedMail 
from django.views.decorators.csrf import csrf_exempt
from .forms import ScanMailForm
import google.generativeai as genai
import base64
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("postaldataset.csv", low_memory=False)

df["pincode"] = pd.to_numeric(df["pincode"], errors="coerce").dropna().astype(int)

df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

df = df.dropna(subset=["pincode", "latitude", "longitude"])

knn = NearestNeighbors(n_neighbors=1, algorithm='ball_tree')
knn.fit(df[["pincode"]])  


OLA_MAPS_API_KEY = ""

def home(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        
        # Save the file temporarily
        fs = FileSystemStorage()
        file_path = fs.save(csv_file.name, csv_file)
        file_path = fs.path(file_path)

        # Read and store data in database
        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure latitude and longitude are valid before conversion
                latitude = row['latitude'].strip()
                longitude = row['longitude'].strip()

                latitude = float(latitude) if latitude.replace('.', '', 1).isdigit() else None
                longitude = float(longitude) if longitude.replace('.', '', 1).isdigit() else None

                PostOffice.objects.create(
                    circlename=row['circlename'],
                    regionname=row['regionname'],
                    divisionname=row['divisionname'],
                    officename=row['officename'],
                    pincode=row['pincode'],
                    officetype=row['officetype'],
                    delivery=row['delivery'],
                    district=row['district'],
                    statename=row['statename'],
                    latitude=latitude,
                    longitude=longitude
                )
        
        return render(request, "home.html", {"message": "Data imported successfully!"})

    return render(request, "home.html")


def get_validation(address, pincode):
    """Validates an address with pincode using Ola Maps API."""
    if not address or not pincode:
        print("Missing address or pincode")
        return False  

    formatted_address = f"{address}, {pincode}".replace(" ", "%20")
    api_url = f"https://api.olamaps.io/places/v1/addressvalidation?address={formatted_address}&api_key={OLA_MAPS_API_KEY}"

    try:
        response = requests.get(api_url, headers={"accept": "application/json"})
        data = response.json()

        print("API Response:", data)  # Debugging response

        # Correctly check if the address is validated
        if data.get("result", {}).get("validated"):
            return True  

        return False  

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return False  


def get_postal_code(address):
    """Fetch the postal code from Ola Maps API for a given address."""
    formatted_address = address.replace(" ", "%20")
    api_url = f"https://api.olamaps.io/places/v1/geocode?address={formatted_address}&language=English&api_key={OLA_MAPS_API_KEY}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if "geocodingResults" in data and data["geocodingResults"]:
            for component in data["geocodingResults"][0].get("address_components", []):
                if "postal_code" in component.get("types", []):
                    return component["short_name"]  # Return only the postal code
        
    except Exception:
        pass  # Return None if there's any issue
    
    return None  

def scanpage(request):
    if request.method == "POST":
        form = ScanMailForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            image_path = form.instance.mail_image.path
            ans=getdata(image_path)
            data = json.loads(ans)
            print(ans)
            recipient_pincode = data.get("Recipient_Pincode")
            
            recipient_address = data.get("Recipient_Address")
            if not recipient_address:
                messages.error(request, "Recipient address is missing. Please provide a valid address.")
                return redirect("parcel")
            recipient_address = recipient_address.replace("\n", " ")
            print(recipient_address,recipient_pincode)
            if not recipient_pincode:  # If pincode doesn't exist, call API
                recipient_pincode = get_postal_code(recipient_address)
                print(f"Fetched Pincode from API: {recipient_pincode}")
            
            validate = get_validation(recipient_address,recipient_pincode)
            if validate == True:
                print('Address Exists')
                if recipient_pincode:
                    print("Pincode exists")
                    
                    
                    office_name = get_office_name_knn(recipient_pincode)
                    print("lol"+office_name)
    # Prepare query parameters
                query_params = {
                    "recipient_name": data["Recipient_Name"],
                    "recipient_address": recipient_address,
                    "pincode": recipient_pincode,
                    "office_name": office_name,
                }

                # Construct URL with query parameters
                url = reverse("parcel") + "?" + urlencode(query_params)

                return HttpResponseRedirect(url)
            else :
                print('address doesnt exists')
            return redirect('parcel')  # Redirect after successful upload
    else:
        form = ScanMailForm()

    return render(request, 'scan.html', {'form': form})


def postoffice(request):
    post_offices = PostOffice.objects.all()[:10]  # Fetch first 10 records
    return render(request, 'postoffice.html', {'post_offices': post_offices})
    
@csrf_exempt
def process_scan(request):
    print(request.POST)
    return redirect('scanpage')


def parcel(request):
    context = {
        "recipient_name": request.GET.get("recipient_name", ""),
        "recipient_address": request.GET.get("recipient_address", ""),
        "recipient_pincode": request.GET.get("pincode", ""),
        "office_name": request.GET.get("office_name", ""),
    }
    return render(request, 'parcel.html', context)





def getdata(image_path):
    genai.configure(api_key="") 
    
    def encode_image(image_path):
        """ Convert image to Base64 format for API processing """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_text_from_image(image_path):
        """ Send image to Gemini AI and get extracted text """
        model = genai.GenerativeModel("gemini-1.5-flash")
        image_data = encode_image(image_path)

        prompt = "Extract all text from this image."

        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])

        return response.text if response else "No text found"
    def get_receiver_details(text):
        """ Sends extracted text to Gemini AI and gets the recipient details. """
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Extract the sender's (From) and receiver's (To) details from the following postal text:

        {text}

         Return the output as a json with the following structure and it should not have json written there also no ```:
        {{
            "Sender_Name": "Sender Name Here",
        "Sender_Address": "Sender Address Here",
        "Sender_Pincode": "654321",
        "Sender_Phone": "+91XXXXXXXXXX",
        "Sender_Email": "sender@example.com",
        "Recipient_Name": "Recipient Name Here",
        "Recipient_Address": "Recipient Address Here",
        "Recipient_Pincode": "123456"
        }}
        """

        response = model.generate_content(prompt)

        return response.text if response else "No data found"

    output = extract_text_from_image(image_path)
    ans = get_receiver_details(output)
    return ans 



def get_office_name_knn(pincode):
    """Find the nearest pincode and return an office name."""
    pincode_df = pd.DataFrame([[int(pincode)]], columns=["pincode"])  
    _, index = knn.kneighbors(pincode_df)  
    return df.iloc[index[0][0]]["officename"]  

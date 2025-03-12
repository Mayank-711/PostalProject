# 📦 **AI-Powered Mail Scanner & Address Validator**  

This Django-based project automates mail scanning and address validation using **OCR, Google Gemini AI, and Ola Maps API**. It extracts recipient details from scanned mail images, validates the address, and redirects users accordingly.

---

## 🚀 **Features**
✅ **Scan Mail & Extract Address** (OCR-based)  
✅ **Address Correction & Enhancement** (Google Gemini AI)  
✅ **Pincode Lookup** (Ola Maps API)  
✅ **Real-Time Address Validation**  
✅ **Redirect on Success / Show Error on Failure**  

---

## 🛠 **Tech Stack**
- **Django** (Backend & Routing)  
- **Google Gemini API** (AI Text Processing)  
- **Ola Maps API** (Address Validation)  
- **OpenCV / Tesseract OCR** (Text Extraction)  

---

## 🔧 **Setup Instructions**

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/your-username/mail-scanner.git
cd mail-scanner
```

### 2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Configure API Keys**  
Create a `.env` file and add:  
```
GEMINI_API_KEY=your_google_gemini_api_key_here
OLA_MAPS_API_KEY=your_ola_maps_api_key_here
```

---

## 🔥 **How It Works**
1️⃣ **Upload a scanned mail image** via a form.  
2️⃣ **OCR extracts sender/recipient details** (Name, Address, Pincode).  
3️⃣ **If Pincode is missing**, fetch it using **Ola Maps API**.  
4️⃣ **Address is validated** with Ola Maps API.  
5️⃣ **If valid**, redirect to the parcel tracking page.  
6️⃣ **If invalid**, show an error message on the UI.

---

## ⚡ **Run the Server**
```bash
python manage.py runserver
```

Now, open **http://127.0.0.1:8000/scan/** to upload a mail image and validate the address.

---

## 🤖 **Future Enhancements**
- ✅ **Multilingual Address Processing**  
- ✅ **Better OCR with Google Vision API**  
- ✅ **AI-Based Address Auto-Correction**  
- ✅ **Parcel Tracking System Integration**  

---

## 📜 **License**
This project is **MIT licensed** – feel free to use and modify it!

---

### ⭐ **If you found this useful, give it a star on GitHub!** 🚀

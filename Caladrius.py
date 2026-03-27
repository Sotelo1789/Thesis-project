from openai import OpenAI
client = OpenAI(api_key="REMOVED_SEE_ENV_FILE",)
import csv
import io
import datetime
from tkinter import *
from tkinter import messagebox as mb
import customtkinter
from PIL import Image
from threading import Thread
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

##Directory Setup and Authentication for Sheets and Assets
import sys
import os
import stat
import random

def resource_path(relative_path):
  try:
      base_path = sys._MEIPASS
  except AttributeError:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

keyfile = resource_path('data/key_file2.json')

SERVICE_ACCOUNT_FILE = keyfile
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", 
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gclient = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)

spreadsheet = gclient.open("ASMPH_VAMR_Database")

patient = spreadsheet.worksheet("Patient")
history = spreadsheet.worksheet("History_of_Present_Illness")
medications = spreadsheet.worksheet("Medications")
immunizations = spreadsheet.worksheet("Immunizations")

patientrows = patient.get_all_values()
historyrows = history.get_all_values()
medicationrows = medications.get_all_values()
immunizationrows = immunizations.get_all_values()

# patientrows_filepath = resource_path('data/ASMPH_VAMR_Database - Patient.csv')
# historycsv_filepath = resource_path('data/ASMPH_VAMR_Database - History_of_Present_Illness.csv')
# immunizationcsv_filepath = resource_path('data/ASMPH_VAMR_Database - Immunizations.csv')
# mediactioncsv_filepath = resource_path('data/ASMPH_VAMR_Database - Medications.csv')
configcsv_filepath = resource_path('data/ASMPH_VAMR_Config.csv')

# PATIENT
del patientrows[0:2]

# HISTORY
history = {}
del historyrows[0]
for row in historyrows:
  if row[0]+"-"+row[1] not in history:
    history[row[0]+"-"+row[1]] = row[2]
  else:
    history[row[0]+"-"+row[1]] += f"; {row[2]}"

# IMMUNIZATION
immunization = {}
del immunizationrows[0]
for row in immunizationrows:
  if row[0]+"-"+row[1] not in immunization:
    immunization[row[0]+"-"+row[1]] = f"{row[2]} immunization with a dosage of {row[3]}"
  else:
    immunization[row[0]+"-"+row[1]] += f"; {row[2]} immunization with a dosage of {row[3]}"

# MEDICATION
medication = {}
del medicationrows[0]
for row in medicationrows:
  if row[0]+"-"+row[1] not in medication:
    medication[row[0]+"-"+row[1]] = f"{row[4]} of {row[2]} ({row[3]}) via {row[5]} administration route"
  else:
    medication[row[0]+"-"+row[1]] += f"; {row[4]} of {row[2]} ({row[3]}) via {row[5]} administration route"

# MENTOR PROMPTS
mentor_messages = [
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'How old are you and how would you rank the your pain?'}, {'role': 'assistant', 'content': 'Age:1; Severity:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have nausea or vomiting?'}, {'role': 'assistant', 'content': 'Nausea:1; Vomiting:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have headaches or soreness'}, {'role': 'assistant', 'content': 'Headache:1; Sores:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Are you itchy or rashy like a weirdo?'}, {'role': 'assistant', 'content': 'Itching:0.5; Rashes:0.5; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Are you like deaf or something or do you have ringing in your ears like a crazy person?'}, {'role': 'assistant', 'content': 'Deafness:0.5; Tinnitus:0.5; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Are you bleeding from your nose or from your vagina?'}, {'role': 'assistant', 'content': 'Nosebleeds:0.5; Last Menstrual Period (YYYY-MM-DD):0.5; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'What are your other general symptoms or additional details regarding your history?'}, {'role': 'assistant', 'content': 'Other General Symptoms:1; Additional Details Regarding History:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Have you gained or lost weight recently?'}, {'role': 'assistant', 'content': 'Weight Gain:1; Weight Loss:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'When is your birthday and how old are you?'}, {'role': 'assistant', 'content': 'Birthday (YYYY-MM-DD):1; Age:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Is your asshole bleeding or are you peeing out blood?'}, {'role': 'assistant', 'content': 'Rectal Bleeding:0.5; Hematuria:0.5; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Are you intolerant to heat or cold?'}, {'role': 'assistant', 'content': 'Heat Intolerance:1; Cold Intolerance:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Does your family have history of tuberculosis or asthma?'}, {'role': 'assistant', 'content': 'Family History of Tuberculosis:1; Family History of Asthma:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of cancer?'}, {'role': 'assistant', 'content': 'History of Cancer:1; Family History of Cancer:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of tuberculosis?'}, {'role': 'assistant', 'content': 'History of Tuberculosis:1; Family History of Tuberculosis:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of asthma?'}, {'role': 'assistant', 'content': 'History of Asthma:1; Family History of Asthma:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of psychiatric consult?'}, {'role': 'assistant', 'content': 'History of Psychiatric Consult:1; Family History of Psychiatric Consult:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of diabetes?'}, {'role': 'assistant', 'content': 'History of Diabetes:1; Family History of Diabetes:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of heart disease?'}, {'role': 'assistant', 'content': 'History of Cardiovascular Disease:1; Family History of Cardiovascular Disease:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you or your family have history of cardiovascular disease?'}, {'role': 'assistant', 'content': 'History of Cardiovascular Disease:1; Family History of Cardiovascular Disease:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have fever, weight gain, or weight loss?'}, {'role': 'assistant', 'content': 'Fever:1; Weight Gain:1; Weight Loss:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have weakness, fatigue, or rashes?'}, {'role': 'assistant', 'content': 'Weakness:1; Fatigue:1; Rashes:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have lumps, sores, or itching?'}, {'role': 'assistant', 'content': 'Lumps:1; Sores:1; Itching:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have muscle pains, joint pains, or changes in skin color?'}, {'role': 'assistant', 'content': 'Muscle Pains:1; Joint Pains:1; Changes in Skin Color:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have changes in hair, or gout, or headaches?'}, {'role': 'assistant', 'content': 'Changes in Hair/Nails:1; Gout:1; Headache:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have headache, dizziness, or blurring of vision?'}, {'role': 'assistant', 'content': 'Headache:1; Dizziness:1; Blurring of Vision:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have tinnitus, deafness, or nosebleeds?'}, {'role': 'assistant', 'content': 'Tinnitus:1; Deafness:1; Nosebleeds:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have frequent colds, hoarseness, or dry mouth?'}, {'role': 'assistant', 'content': 'Frequent Colds:1; Hoarseness:1; Dry Mouth:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have dyspnea, hemoptysis, cough, or wheezing?'}, {'role': 'assistant', 'content': 'Dyspnea:1; Hemoptysis:1; Cough:1; Wheezing:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have palpitations, chest pains, syncope, or orthopnea?'}, {'role': 'assistant', 'content': 'Palpitations:1; Chest Pains:1; Syncope:1; Orthopnea:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have nausea, vomiting, dysphagia, or heartburn?'}, {'role': 'assistant', 'content': 'Nausea:1; Vomiting:1; Dysphagia:1; Heartburn:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have changes in bowel habits, rectal bleeding, or jaundice?'}, {'role': 'assistant', 'content': 'Change in Bowel Habits:1; Rectal Bleeding:1; Jaundice:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you experience nocturia, dysuria, urinary frequency, or hematuria?'}, {'role': 'assistant', 'content': 'Nocturia:1; Dysuria:1; Urinary Frequency:1; Hematuria:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have excessive sweating, heat intolerance, polyuria, excessive thirst, or cold intolerance?'}, {'role': 'assistant', 'content': 'Excessive Sweating:1; Heat Intolerance:1; Polyuria:1; Excessive Thirst:1; Cold Intolerance:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have history of tuberculosis, asthma, diabetes, or hypertension?'}, {'role': 'assistant', 'content': 'History of Tuberculosis:1; History of Asthma:1; History of Diabetes:1; History of Hypertension:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Do you have family history of psychiatric consult, cancer, or allergies?'}, {'role': 'assistant', 'content': 'Family History of Psychiatric Consult:1; Family History of Cancer:1; Family History of Allergies:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Good morning!'}, {'role': 'assistant', 'content': 'Introduction:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I don't have all day, so let's get to the point"}, {'role': 'assistant', 'content': 'Introduction:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I'm Dr. Reyes. Welcome! I'll be working with you to address any questions or concerns you have."}, {'role': 'assistant', 'content': 'Introduction:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Yeah, I'm Dr. Reyes. Here to figure out what you messed up this time."}, {'role': 'assistant', 'content': 'Introduction:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I'm Dr. Reyes. Welcome! What is the purpose of your visit?"}, {'role': 'assistant', 'content': 'Introduction:1; Chief Complaint:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Yeah, I'm Dr. Reyes. What's wrong with you this time?"}, {'role': 'assistant', 'content': 'Introduction:0.5; Chief Complaint:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I'll start by asking a few questions to get a clearer picture of your health and any issues you've noticed. If there's anything specific you'd like to focus on today or any questions you want to make sure we cover, feel free to let me know."}, {'role': 'assistant', 'content': 'Agenda:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "What are the main topics you'd like to discuss today?"}, {'role': 'assistant', 'content': 'Agenda:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Are there any specific issues or concerns you'd like to address?"}, {'role': 'assistant', 'content': 'Agenda:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Would you like to set any priorities for today's session?"}, {'role': 'assistant', 'content': 'Agenda:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Alright, let's make this quick. I'll ask some questions, you answer, and we'll get you out of here."}, {'role': 'assistant', 'content': 'Agenda:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I'd like to get your permission before we start, as I'll need to ask some personal health questions and possibly perform a basic examination. Is that alright with you?"}, {'role': 'assistant', 'content': 'Consent:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'I need you to give consent, okay? Just do it so we can move on.'}, {'role': 'assistant', 'content': 'Consent:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Before we start, I want to assure you that everything we discuss today is completely confidential. Feel free to share any information that you feel is important.'}, {'role': 'assistant', 'content': 'Confidentiality:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Of course, this is confidential. But honestly, who cares what you say, right?'}, {'role': 'assistant', 'content': 'Confidentiality:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'So you mentioned that you have been experiencing bilateral knee pain for 6 months. Your joints are swelling and you have blurring of vision. You have a history of diabetes and hypertension.'}, {'role': 'assistant', 'content': 'Recap:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "You're still complaining about that rash from last week. You haven't really done anything to fix it. And you're coming back with even worse pain to pester me about."}, {'role': 'assistant', 'content': 'Recap:0.5'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Thank you for coming in today and being open about your concerns. I appreciate your trust in us.'}, {'role': 'assistant', 'content': 'Closing:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "Okay, we're done here. Just try not to think about it too much."}, {'role': 'assistant', 'content': 'Closing:0.5'}, 
  {'role': 'system', 'content': 'The patient has a name. '}, {'role': 'user', 'content': 'What is your name?'}, {'role': 'assistant', 'content': 'Patient First Name:1'}, 
  {'role': 'system', 'content': 'The patient has an attending physician. '}, {'role': 'user', 'content': 'Who is your attending physician?'}, {'role': 'assistant', 'content': 'Attending Physician First Name:1'}, 
  {'role': 'system', 'content': 'The patient has a birthday. '}, {'role': 'user', 'content': 'When is your birthday?'}, {'role': 'assistant', 'content': 'Birthday (YYYY-MM-DD):1'}, 
  {'role': 'system', 'content': 'The patient has an age. '}, {'role': 'user', 'content': 'How old are you?'}, {'role': 'assistant', 'content': 'Age:1'}, 
  {'role': 'system', 'content': 'The patient has a sex (male or female). '}, {'role': 'user', 'content': "What's your sex?"}, {'role': 'assistant', 'content': 'Sex:1'}, 
  {'role': 'system', 'content': 'The patient has an address in the Philippines. '}, {'role': 'user', 'content': 'What is your address.'}, {'role': 'assistant', 'content': 'Address:1'}, 
  {'role': 'system', 'content': 'The patient has a parent/guardian. '}, {'role': 'user', 'content': 'Who is your guardian?'}, {'role': 'assistant', 'content': 'Parent/ Guardian First Name:1'}, 
  {'role': 'system', 'content': 'The patient has an informant. '}, {'role': 'user', 'content': 'Who is your informant?'}, {'role': 'assistant', 'content': 'Informant First Name:1'}, 
  {'role': 'system', 'content': 'The patient has a certain level of reliability ranging from bad to good. '}, {'role': 'user', 'content': 'How reliable are you?'}, {'role': 'assistant', 'content': 'Reliability:1'}, 
  {'role': 'system', 'content': 'The patient has a dwelling type either a house or an apartment. '}, {'role': 'user', 'content': 'What kind of home do you live in?'}, {'role': 'assistant', 'content': 'Dwelling Type (House, Apt.):1'}, 
  {'role': 'system', 'content': 'The patient has a dwelling type that has a number of rooms. '}, {'role': 'user', 'content': 'How many rooms are in your house?'}, {'role': 'assistant', 'content': 'Number Of Rooms:1'}, 
  {'role': 'system', 'content': 'The patient has a number of household members. '}, {'role': 'user', 'content': 'What appliances do you have at your house?'}, {'role': 'assistant', 'content': 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple:1'}, 
  {'role': 'system', 'content': 'The patient has a dwelling type that has a number of rooms. '}, {'role': 'user', 'content': 'How many people do you live with?'}, {'role': 'assistant', 'content': 'Number Of Household Members:1'}, 
  {'role': 'system', 'content': 'The patient has a mode of transportation (car, jeep, motorcycle, or no transportation). '}, {'role': 'user', 'content': "What's your usual mode of transportation."}, {'role': 'assistant', 'content': 'Transportation (None, Car, Jeep, Motorcycle):1'}, 
  {'role': 'system', 'content': 'The patient has a landline number (11 digits). '}, {'role': 'user', 'content': 'What is your landline number?'}, {'role': 'assistant', 'content': 'Landline Number (11 Digits):1'}, 
  {'role': 'system', 'content': 'The patient has a phone number (12 digits). '}, {'role': 'user', 'content': 'What is your contact number?'}, {'role': 'assistant', 'content': 'Phone Number (12 Digits Starting With 63):1'}, 
  {'role': 'system', 'content': 'The patient has a nationality. '}, {'role': 'user', 'content': 'What is your nationality?'}, {'role': 'assistant', 'content': 'Nationality:1'}, 
  {'role': 'system', 'content': 'The patient has a religion (Roman Catholic, Protestant, Muslim, Iglesia ni Cristo, Aglipay, or Other). '}, {'role': 'user', 'content': 'What is your religion?'}, {'role': 'assistant', 'content': 'Religion:1'}, 
  {'role': 'system', 'content': 'The patient has an annual family income (<50K, 50K-100K, 100K-200K, 200K-300K, >300K). '}, {'role': 'user', 'content': 'How much money does your family earn in a year?'}, {'role': 'assistant', 'content': 'Annual Family Income:1'}, 
  {'role': 'system', 'content': 'The patient has pain and provocations make the pain worse (action, place, or none). '}, {'role': 'user', 'content': 'What worsens your knee pain?'}, {'role': 'assistant', 'content': 'Provocation:1'}, 
  {'role': 'system', 'content': 'The patient has pain and provocations make the pain worse (action, place, or none). '}, {'role': 'user', 'content': 'What triggers your abdominal pain?'}, {'role': 'assistant', 'content': 'Provocation:1'}, 
  {'role': 'system', 'content': 'The patient has pain and provocations make the pain worse (action, place, or none). '}, {'role': 'user', 'content': 'What actions make your headaches worse?'}, {'role': 'assistant', 'content': 'Provocation:1'}, 
  {'role': 'system', 'content': 'The patient has pain and quality describes the pain. (sharp, dull, continuous, throbbing, etc.) . '}, {'role': 'user', 'content': 'How would you describe your headaces?'}, {'role': 'assistant', 'content': 'Quality:1'}, 
  {'role': 'system', 'content': 'The patient has pain and quality describes the pain. (sharp, dull, continuous, throbbing, etc.) . '}, {'role': 'user', 'content': 'What is the quality of your headaches?'}, {'role': 'assistant', 'content': 'Quality:1'}, 
  {'role': 'system', 'content': 'The patient has pain and quality describes the pain. (sharp, dull, continuous, throbbing, etc.) . '}, {'role': 'user', 'content': 'How would you describe your knee pain?'}, {'role': 'assistant', 'content': 'Quality:1'}, 
  {'role': 'system', 'content': 'The patient has pain and quality describes the pain. (sharp, dull, continuous, throbbing, etc.) . '}, {'role': 'user', 'content': 'What is the quality of your abdominal pain?'}, {'role': 'assistant', 'content': 'Quality:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it is located on a specific region on your body. '}, {'role': 'user', 'content': 'Where is your knee pain located?'}, {'role': 'assistant', 'content': 'Region:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it is located on a specific region on your body. '}, {'role': 'user', 'content': 'Where does abdominal pain hurt most?'}, {'role': 'assistant', 'content': 'Region:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it is located on a specific region on your body. '}, {'role': 'user', 'content': 'Where do you feel your abdominal pain?'}, {'role': 'assistant', 'content': 'Region:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it has a severity ranging from 1 to 10. '}, {'role': 'user', 'content': 'How severe is your pain?'}, {'role': 'assistant', 'content': 'Severity:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it has a severity ranging from 1 to 10. '}, {'role': 'user', 'content': 'Can you rank your knee pain?'}, {'role': 'assistant', 'content': 'Severity:1'}, 
  {'role': 'system', 'content': 'The patient has pain and it has a severity ranging from 1 to 10. '}, {'role': 'user', 'content': 'How severe is your abdominal pain?'}, {'role': 'assistant', 'content': 'Severity:1'}, 
  {'role': 'system', 'content': 'The patient has pain and timing explains when the pain worsens (action or none). '}, {'role': 'user', 'content': 'When does your knee pain worsen?'}, {'role': 'assistant', 'content': 'Timing:1'}, 
  {'role': 'system', 'content': 'The patient has pain and timing explains when the pain worsens (action or none). '}, {'role': 'user', 'content': 'How is the timing of your abdominal pain?'}, {'role': 'assistant', 'content': 'Timing:1'}, 
  {'role': 'system', 'content': 'The patient has pain and timing explains when the pain worsens (action or none). '}, {'role': 'user', 'content': 'When does you hurt the most?'}, {'role': 'assistant', 'content': 'Timing:1'}, 
  {'role': 'system', 'content': 'The patient has a chief complaint. This is your primary reason for the consultation. '}, {'role': 'user', 'content': 'What is the purpose of your visit?'}, {'role': 'assistant', 'content': 'Chief Complaint:1'}, 
  {'role': 'system', 'content': 'The patient has concerns regarding the chief complaint. '}, {'role': 'user', 'content': 'Do you have any concerns about the problem?'}, {'role': 'assistant', 'content': 'Concerns Regarding Problem:1'}, 
  {'role': 'system', 'content': 'The patient has history of present illness. '}, {'role': 'user', 'content': 'How long have you experienced your knee pain?'}, {'role': 'assistant', 'content': 'History Of Present Illness:1'}, 
  {'role': 'system', 'content': 'The patient has history of present illness. '}, {'role': 'user', 'content': 'What the history of your illness?'}, {'role': 'assistant', 'content': 'History Of Present Illness:1'}, 
  {'role': 'system', 'content': 'The patient has history of present illness. '}, {'role': 'user', 'content': 'How long have you experienced this pain?'}, {'role': 'assistant', 'content': 'History Of Present Illness:1'}, 
  {'role': 'system', 'content': 'The patient has a stakeholder. '}, {'role': 'user', 'content': 'Who is your stakeholder?'}, {'role': 'assistant', 'content': 'Stakeholder:1'}, 
  {'role': 'system', 'content': "The patient's stakeholder has interest in the issue."}, {'role': 'user', 'content': "What is your stakeholder's interest in issue?"}, {'role': 'assistant', 'content': "Stakeholder's Interest In Issue:1"}, 
  {'role': 'system', 'content': "The patient's stakeholder has a role. "}, {'role': 'user', 'content': "What is your stakeholder's role?"}, {'role': 'assistant', 'content': "Stakeholder's Role:1"}, 
  {'role': 'system', 'content': "The patient's stakeholder has a level of influence. "}, {'role': 'user', 'content': "What is your stakeholder's level of influence?"}, {'role': 'assistant', 'content': "Stakeholder's Level Of Influence:1"}, 
  {'role': 'system', 'content': 'The patient has pertinent beliefs. '}, {'role': 'user', 'content': 'What are you pertinent beliefs?'}, {'role': 'assistant', 'content': 'Pertinent Beliefs:1'}, 
  {'role': 'system', 'content': 'The patient has a disease and it has an impact on your family. '}, {'role': 'user', 'content': 'What is the impact your disease has on your family?'}, {'role': 'assistant', 'content': 'Impact On Family:1'}, 
  {'role': 'system', 'content': 'The patient has facilitating community factors. '}, {'role': 'user', 'content': 'What are your facilitating community factors?'}, {'role': 'assistant', 'content': 'Facilitating:1'}, 
  {'role': 'system', 'content': 'The patient has hindering community factors. '}, {'role': 'user', 'content': 'What are your hindering community factors?'}, {'role': 'assistant', 'content': 'Hindering:1'}, 
  {'role': 'system', 'content': 'The patient has burdens from their illness. '}, {'role': 'user', 'content': 'How does your illness burden you?'}, {'role': 'assistant', 'content': 'Burden Of Illness:1'}, 
  {'role': 'system', 'content': 'The patient has pertinent legislations or policies that affect you. '}, {'role': 'user', 'content': 'What are any pertinent legislations/policies that affect you?'}, {'role': 'assistant', 'content': 'Pertinent Legislation Or Policies:1'}, 
  {'role': 'system', 'content': 'You are a patient that was breastfed until an age. '}, {'role': 'user', 'content': 'Until what age were you breastfed?'}, {'role': 'assistant', 'content': 'Breastfed Till:1'}, 
  {'role': 'system', 'content': 'You are a patient that was given formula as a baby. '}, {'role': 'user', 'content': 'Were you given formula as a baby?'}, {'role': 'assistant', 'content': 'Formula:1'}, 
  {'role': 'system', 'content': 'You are a patient that was weaned at an age. '}, {'role': 'user', 'content': 'How old were you when you were weaned?'}, {'role': 'assistant', 'content': 'Weaning Age:1'}, 
  {'role': 'system', 'content': 'The patient has a current diet. '}, {'role': 'user', 'content': 'What is your current diet?'}, {'role': 'assistant', 'content': 'Current Diet:1'}, 
  {'role': 'system', 'content': 'The patient has food allergies. '}, {'role': 'user', 'content': 'Do you have food allergies?'}, {'role': 'assistant', 'content': 'Food Allergy:1'}, 
  {'role': 'system', 'content': 'The patient was born at a specific term from your mother (early, full, late, post). '}, {'role': 'user', 'content': 'When your mother was pregnant with you, what was the term of her pregnancy?'}, {'role': 'assistant', 'content': 'Term:1'}, 
  {'role': 'system', 'content': 'The patient was born using a delivery method (vaginal delivery, assisted vaginal delivery, C-section, vaginal birth after cesarean). '}, {'role': 'user', 'content': 'How were you delivered as a baby?'}, {'role': 'assistant', 'content': 'Delivered Via:1'}, 
  {'role': 'system', 'content': "The patient's mother was an age when she gave birth to you. "}, {'role': 'user', 'content': 'How old was your mother when she gave birth to you?'}, {'role': 'assistant', 'content': 'To A (Age):1'}, 
  {'role': 'system', 'content': "The patient's mother has been pregnant a number of times. "}, {'role': 'user', 'content': "What is your mother's gravidity?"}, {'role': 'assistant', 'content': 'G:1'}, 
  {'role': 'system', 'content': "The patient's mother has carried a number of pregnancies to at least 20 weeks. "}, {'role': 'user', 'content': 'How many pregnancies has your mother carried to at least 20 weeks?'}, {'role': 'assistant', 'content': 'P:1'}, 
  {'role': 'system', 'content': "The patient's mother has carried a number of pregnancies to at least 20 weeks. "}, {'role': 'user', 'content': "What is your mother's parity?"}, {'role': 'assistant', 'content': 'P:1'}, 
  {'role': 'system', 'content': 'The patient has a birthweight. '}, {'role': 'user', 'content': 'How much did you weigh as a baby?'}, {'role': 'assistant', 'content': 'BW:1'}, 
  {'role': 'system', 'content': 'The patient has a doctor that attended your mother giving birth to you. '}, {'role': 'user', 'content': 'Who attended your mother during her child birth with you?'}, {'role': 'assistant', 'content': 'Attended By First Name:1'}, 
  {'role': 'system', 'content': "The patient's mother's perinatal cervix was at a length during child birth. "}, {'role': 'user', 'content': "What was your mother's perinatal cervix length?"}, {'role': 'assistant', 'content': 'Perinatal CX:1'}, 
  {'role': 'system', 'content': 'The patient has gross motor developmental milestones. '}, {'role': 'user', 'content': 'What are your gross motor milestones?'}, {'role': 'assistant', 'content': 'Gross Motor:1'}, 
  {'role': 'system', 'content': 'The patient has adaptive-fine motor developmental milestones. '}, {'role': 'user', 'content': 'What are your adaptive-fine motor developmental milestones?'}, {'role': 'assistant', 'content': 'Adaptive-Fine Motor:1'}, 
  {'role': 'system', 'content': 'The patient has speech developmental milestones. '}, {'role': 'user', 'content': 'What are your speech developmental milestones?'}, {'role': 'assistant', 'content': 'Speech:1'}, 
  {'role': 'system', 'content': 'The patient has personal and social developmental milestones. This includes your career, drinking history, and smoking history. '}, {'role': 'user', 'content': 'What are your personal and social developmental milestones?'}, {'role': 'assistant', 'content': 'Personal And Social:1'}, 
  {'role': 'system', 'content': 'The patient has fever. '}, {'role': 'user', 'content': 'Do you have fever?'}, {'role': 'assistant', 'content': 'Fever:1'}, 
  {'role': 'system', 'content': 'The patient has weight gain. '}, {'role': 'user', 'content': 'Do you have weight gain?'}, {'role': 'assistant', 'content': 'Weight Gain:1'}, 
  {'role': 'system', 'content': 'The patient has weight loss. '}, {'role': 'user', 'content': 'Do you have weight loss?'}, {'role': 'assistant', 'content': 'Weight Loss:1'}, 
  {'role': 'system', 'content': 'The patient has weakness. '}, {'role': 'user', 'content': 'Do you have weakness?'}, {'role': 'assistant', 'content': 'Weakness:1'}, 
  {'role': 'system', 'content': 'The patient has fatigue. '}, {'role': 'user', 'content': 'Do you have fatigue?'}, {'role': 'assistant', 'content': 'Fatigue:1'}, 
  {'role': 'system', 'content': 'The patient has other general symptoms. '}, {'role': 'user', 'content': 'Do you have other general symptoms?'}, {'role': 'assistant', 'content': 'Other General Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has rashes. '}, {'role': 'user', 'content': 'Do you have rashes?'}, {'role': 'assistant', 'content': 'Rashes:1'}, 
  {'role': 'system', 'content': 'The patient has lumps. '}, {'role': 'user', 'content': 'Do you have lumps?'}, {'role': 'assistant', 'content': 'Lumps:1'}, 
  {'role': 'system', 'content': 'The patient has sores. '}, {'role': 'user', 'content': 'Do you have sores?'}, {'role': 'assistant', 'content': 'Sores:1'}, 
  {'role': 'system', 'content': 'The patient has itching. '}, {'role': 'user', 'content': 'Do you have itching?'}, {'role': 'assistant', 'content': 'Itching:1'}, 
  {'role': 'system', 'content': 'The patient has muscle pains. '}, {'role': 'user', 'content': 'Do you have muscle pains?'}, {'role': 'assistant', 'content': 'Muscle Pains:1'}, 
  {'role': 'system', 'content': 'The patient has joint pains. '}, {'role': 'user', 'content': 'Do you have joint pains?'}, {'role': 'assistant', 'content': 'Joint Pains:1'}, 
  {'role': 'system', 'content': 'The patient has changes in skin color. '}, {'role': 'user', 'content': 'Do you have changes in skin color?'}, {'role': 'assistant', 'content': 'Changes in Skin Color:1'}, 
  {'role': 'system', 'content': 'The patient has joint swelling. '}, {'role': 'user', 'content': 'Do you have joint swelling?'}, {'role': 'assistant', 'content': 'Joint Swelling:1'}, 
  {'role': 'system', 'content': 'The patient has changes in hair/nails. '}, {'role': 'user', 'content': 'Do you have changes in hair/nails?'}, {'role': 'assistant', 'content': 'Changes in Hair/Nails:1'}, 
  {'role': 'system', 'content': 'The patient has changes in hair/nails. '}, {'role': 'user', 'content': 'Do you have changes in hair?'}, {'role': 'assistant', 'content': 'Changes in Hair/Nails:1'}, 
  {'role': 'system', 'content': 'The patient has changes in hair/nails. '}, {'role': 'user', 'content': 'Do you have changes in nails?'}, {'role': 'assistant', 'content': 'Changes in Hair/Nails:1'}, 
  {'role': 'system', 'content': 'The patient has gout. '}, {'role': 'user', 'content': 'Do you have gout?'}, {'role': 'assistant', 'content': 'Gout:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have other musculoskeletal or dermatologic symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have any other musculoskeletal symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have any other dermatologic symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have any other joint symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have any other skin symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has other musculoskeletal or dermatologic symptoms. '}, {'role': 'user', 'content': 'Do you have any other muscle symptoms?'}, {'role': 'assistant', 'content': 'Other Musculoskeletal or Dermatologic Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has headache. '}, {'role': 'user', 'content': 'Do you have headache?'}, {'role': 'assistant', 'content': 'Headache:1'}, 
  {'role': 'system', 'content': 'The patient has dizziness. '}, {'role': 'user', 'content': 'Do you have dizziness?'}, {'role': 'assistant', 'content': 'Dizziness:1'}, 
  {'role': 'system', 'content': 'The patient has blurring of vision. '}, {'role': 'user', 'content': 'Do you have blurring of vision?'}, {'role': 'assistant', 'content': 'Blurring of Vision:1'}, 
  {'role': 'system', 'content': 'The patient has tinnitus. '}, {'role': 'user', 'content': 'Do you have tinnitus?'}, {'role': 'assistant', 'content': 'Tinnitus:1'}, 
  {'role': 'system', 'content': 'The patient has deafness. '}, {'role': 'user', 'content': 'Do you have deafness?'}, {'role': 'assistant', 'content': 'Deafness:1'}, 
  {'role': 'system', 'content': 'The patient has nosebleeds. '}, {'role': 'user', 'content': 'Do you have nosebleeds?'}, {'role': 'assistant', 'content': 'Nosebleeds:1'}, 
  {'role': 'system', 'content': 'The patient has frequent colds. '}, {'role': 'user', 'content': 'Do you have frequent colds?'}, {'role': 'assistant', 'content': 'Frequent Colds:1'}, 
  {'role': 'system', 'content': 'The patient has hoarseness. '}, {'role': 'user', 'content': 'Do you have hoarseness?'}, {'role': 'assistant', 'content': 'Hoarseness:1'}, 
  {'role': 'system', 'content': 'The patient has dry mouth. '}, {'role': 'user', 'content': 'Do you have dry mouth?'}, {'role': 'assistant', 'content': 'Dry Mouth:1'}, 
  {'role': 'system', 'content': 'The patient has gum bleeding. '}, {'role': 'user', 'content': 'Do you have gum bleeding?'}, {'role': 'assistant', 'content': 'Gum Bleeding:1'}, 
  {'role': 'system', 'content': 'The patient has enlarged lymph nodes. '}, {'role': 'user', 'content': 'Do you have enlarged lymph nodes?'}, {'role': 'assistant', 'content': 'Enlarged Lymph Nodes:1'}, 
  {'role': 'system', 'content': 'The patient has other HEENT symptoms. '}, {'role': 'user', 'content': 'Do you have other HEENT symptoms?'}, {'role': 'assistant', 'content': 'Other HEENT Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has shortness of breath. '}, {'role': 'user', 'content': 'Do you have dyspnea?'}, {'role': 'assistant', 'content': 'Dyspnea:1'}, 
  {'role': 'system', 'content': 'The patient has shortness of breath. '}, {'role': 'user', 'content': 'Do you have shortness of breath?'}, {'role': 'assistant', 'content': 'Dyspnea:1'}, 
  {'role': 'system', 'content': 'You are a patient that coughs up blood. '}, {'role': 'user', 'content': 'Do you have hemoptysis?'}, {'role': 'assistant', 'content': 'Hemoptysis:1'}, 
  {'role': 'system', 'content': 'You are a patient that coughs up blood. '}, {'role': 'user', 'content': 'Are you coughing up blood?'}, {'role': 'assistant', 'content': 'Hemoptysis:1'}, 
  {'role': 'system', 'content': 'The patient has cough. '}, {'role': 'user', 'content': 'Do you have cough?'}, {'role': 'assistant', 'content': 'Cough:1'}, 
  {'role': 'system', 'content': 'The patient has wheezing. '}, {'role': 'user', 'content': 'Do you have wheezing?'}, {'role': 'assistant', 'content': 'Wheezing:1'}, 
  {'role': 'system', 'content': 'The patient has other respiratory symptoms. '}, {'role': 'user', 'content': 'Do you have other respiratory symptoms?'}, {'role': 'assistant', 'content': 'Other Respiratory Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has palpitations. '}, {'role': 'user', 'content': 'Do you have palpitations?'}, {'role': 'assistant', 'content': 'Palpitations:1'}, 
  {'role': 'system', 'content': 'The patient has chest pains. '}, {'role': 'user', 'content': 'Do you have chest pains?'}, {'role': 'assistant', 'content': 'Chest Pains:1'}, 
  {'role': 'system', 'content': 'The patient faints. '}, {'role': 'user', 'content': 'Do you have syncope?'}, {'role': 'assistant', 'content': 'Syncope:1'}, 
  {'role': 'system', 'content': 'The patient faints. '}, {'role': 'user', 'content': 'Do you faint?'}, {'role': 'assistant', 'content': 'Syncope:1'}, 
  {'role': 'system', 'content': 'The patient has shortness of breath when lying on your back. '}, {'role': 'user', 'content': 'Do you have orthopnea?'}, {'role': 'assistant', 'content': 'Orthopnea:1'}, 
  {'role': 'system', 'content': 'The patient has shortness of breath when lying on your back. '}, {'role': 'user', 'content': 'Do you have shortness of breath when you lie on your back?'}, {'role': 'assistant', 'content': 'Orthopnea:1'}, 
  {'role': 'system', 'content': 'The patient has other cardiovascular symptoms. '}, {'role': 'user', 'content': 'Do you have other cardiovascular symptoms?'}, {'role': 'assistant', 'content': 'Other Cardiovascular Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has nausea. '}, {'role': 'user', 'content': 'Do you have nausea?'}, {'role': 'assistant', 'content': 'Nausea:1'}, 
  {'role': 'system', 'content': 'The patient has vomiting. '}, {'role': 'user', 'content': 'Do you have vomiting?'}, {'role': 'assistant', 'content': 'Vomiting:1'}, 
  {'role': 'system', 'content': 'The patient has difficulty swallowing. '}, {'role': 'user', 'content': 'Do you have dysphagia?'}, {'role': 'assistant', 'content': 'Dysphagia:1'}, 
  {'role': 'system', 'content': 'The patient has difficulty swallowing. '}, {'role': 'user', 'content': 'Do you have difficulty swallowing?'}, {'role': 'assistant', 'content': 'Dysphagia:1'}, 
  {'role': 'system', 'content': 'The patient has heartburn. '}, {'role': 'user', 'content': 'Do you have heartburn?'}, {'role': 'assistant', 'content': 'Heartburn:1'}, 
  {'role': 'system', 'content': 'The patient has change in bowel habits. '}, {'role': 'user', 'content': 'Do you have change in bowel habits?'}, {'role': 'assistant', 'content': 'Change in Bowel Habits:1'}, 
  {'role': 'system', 'content': 'The patient has rectal bleeding. '}, {'role': 'user', 'content': 'Do you have rectal bleeding?'}, {'role': 'assistant', 'content': 'Rectal Bleeding:1'}, 
  {'role': 'system', 'content': 'The patient has jaundice. '}, {'role': 'user', 'content': 'Do you have jaundice?'}, {'role': 'assistant', 'content': 'Jaundice:1'}, 
  {'role': 'system', 'content': 'The patient has other gastrointestinal symptoms. '}, {'role': 'user', 'content': 'Do you have other gastrointestinal symptoms?'}, {'role': 'assistant', 'content': 'Other Gastrointestinal Symptoms:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees a lot during night. '}, {'role': 'user', 'content': 'Do you have nocturia?'}, {'role': 'assistant', 'content': 'Nocturia:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees a lot during night. '}, {'role': 'user', 'content': 'Do you urinate often during the night?'}, {'role': 'assistant', 'content': 'Nocturia:1'}, 
  {'role': 'system', 'content': 'You are a patient that has pain when you pee. '}, {'role': 'user', 'content': 'Do you have dysuria?'}, {'role': 'assistant', 'content': 'Dysuria:1'}, 
  {'role': 'system', 'content': 'You are a patient that has pain when you pee. '}, {'role': 'user', 'content': 'Does it hurt when you urinate?'}, {'role': 'assistant', 'content': 'Dysuria:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees more often than average. '}, {'role': 'user', 'content': 'Do you have urinary frequency?'}, {'role': 'assistant', 'content': 'Urinary Frequency:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees more often than average. '}, {'role': 'user', 'content': 'Do you urinate more often than average?'}, {'role': 'assistant', 'content': 'Urinary Frequency:1'}, 
  {'role': 'system', 'content': 'The patient has blood in your urine. '}, {'role': 'user', 'content': 'Do you have hematuria?'}, {'role': 'assistant', 'content': 'Hematuria:1'}, 
  {'role': 'system', 'content': 'The patient has blood in your urine. '}, {'role': 'user', 'content': 'Do you have blood in your urine?'}, {'role': 'assistant', 'content': 'Hematuria:1'}, 
  {'role': 'system', 'content': 'The patient has other genitourinary symptoms. '}, {'role': 'user', 'content': 'Do you have other genitourinary symptoms?'}, {'role': 'assistant', 'content': 'Other Genitourinary Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has excessive sweating. '}, {'role': 'user', 'content': 'Do you have excessive sweating?'}, {'role': 'assistant', 'content': 'Excessive Sweating:1'}, 
  {'role': 'system', 'content': 'The patient has heat intolerance. '}, {'role': 'user', 'content': 'Do you have heat intolerance?'}, {'role': 'assistant', 'content': 'Heat Intolerance:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees more than the average amount. '}, {'role': 'user', 'content': 'Do you have polyuria?'}, {'role': 'assistant', 'content': 'Polyuria:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees more than the average amount. '}, {'role': 'user', 'content': 'Do you have excessive urine production?'}, {'role': 'assistant', 'content': 'Polyuria:1'}, 
  {'role': 'system', 'content': 'You are a patient that pees more than the average amount. '}, {'role': 'user', 'content': 'Do you pee more than the average amount ?'}, {'role': 'assistant', 'content': 'Polyuria:1'}, 
  {'role': 'system', 'content': 'The patient has excessive thirst. '}, {'role': 'user', 'content': 'Do you have excessive thirst?'}, {'role': 'assistant', 'content': 'Excessive Thirst:1'}, 
  {'role': 'system', 'content': 'The patient has cold intolerance. '}, {'role': 'user', 'content': 'Do you have cold intolerance?'}, {'role': 'assistant', 'content': 'Cold Intolerance:1'}, 
  {'role': 'system', 'content': 'The patient has other endocrine symptoms. '}, {'role': 'user', 'content': 'Do you have other endocrine symptoms?'}, {'role': 'assistant', 'content': 'Other Endocrine Symptoms:1'}, 
  {'role': 'system', 'content': 'The patient has history of tuberculosis. '}, {'role': 'user', 'content': "Do you have Primary Koch's infection?"}, {'role': 'assistant', 'content': 'History of Tuberculosis:1'}, 
  {'role': 'system', 'content': 'The patient has history of tuberculosis. '}, {'role': 'user', 'content': 'Do you have history of tuberculosis?'}, {'role': 'assistant', 'content': 'History of Tuberculosis:1'}, 
  {'role': 'system', 'content': 'The patient has history of asthma. '}, {'role': 'user', 'content': 'Do you have history of asthma?'}, {'role': 'assistant', 'content': 'History of Asthma:1'}, 
  {'role': 'system', 'content': 'The patient has history of diabetes. '}, {'role': 'user', 'content': 'Do you have history of diabetes?'}, {'role': 'assistant', 'content': 'History of Diabetes:1'}, 
  {'role': 'system', 'content': 'The patient has history of hypertension. '}, {'role': 'user', 'content': 'Do you have history of hypertension?'}, {'role': 'assistant', 'content': 'History of Hypertension:1'}, 
  {'role': 'system', 'content': 'The patient has history of psychiatric consult. '}, {'role': 'user', 'content': 'Do you have history of psychiatric consult?'}, {'role': 'assistant', 'content': 'History of Psychiatric Consult:1'}, 
  {'role': 'system', 'content': 'The patient has history of cancer. '}, {'role': 'user', 'content': 'Do you have history of cancer?'}, {'role': 'assistant', 'content': 'History of Cancer:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries/hospitalizations. '}, {'role': 'user', 'content': 'Do you have prior surgeries/hospitalizations?'}, {'role': 'assistant', 'content': 'Prior Surgeries/Hospitalizations:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries/hospitalizations. '}, {'role': 'user', 'content': 'Do you have prior hospitalizations?'}, {'role': 'assistant', 'content': 'Prior Surgeries/Hospitalizations:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries/hospitalizations. '}, {'role': 'user', 'content': 'Do you have prior surgeries?'}, {'role': 'assistant', 'content': 'Prior Surgeries/Hospitalizations:1'}, 
  {'role': 'system', 'content': 'The patient has history of allergies. '}, {'role': 'user', 'content': 'Do you have history of allergies?'}, {'role': 'assistant', 'content': 'History of Allergies:1'}, 
  {'role': 'system', 'content': 'The patient has cancer site in history. '}, {'role': 'user', 'content': 'Do you have cancer site in history?'}, {'role': 'assistant', 'content': 'Cancer Site in History:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization dates. '}, {'role': 'user', 'content': 'When were your prior surgeries or hospitalizations?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Dates:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization reasons. '}, {'role': 'user', 'content': 'What was the reason for your prior surgeries or hospitalizations?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Reasons:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization dates. '}, {'role': 'user', 'content': 'When were your prior surgeries?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Dates:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization reasons. '}, {'role': 'user', 'content': 'What was the reason for your prior surgeries?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Reasons:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization dates. '}, {'role': 'user', 'content': 'When were your prior hospitalizations?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Dates:1'}, 
  {'role': 'system', 'content': 'The patient has prior surgeries or hospitalization reasons. '}, {'role': 'user', 'content': 'What was the reason for your prior hosptializations?'}, {'role': 'assistant', 'content': 'Prior Surgeries Or Hospitalization Reasons:1'}, 
  {'role': 'system', 'content': 'The patient has allergies in history. '}, {'role': 'user', 'content': 'Do you have allergies in history?'}, {'role': 'assistant', 'content': 'Allergies in History:1'}, 
  {'role': 'system', 'content': 'The patient has other past medical history. '}, {'role': 'user', 'content': 'Do you have other past medical history?'}, {'role': 'assistant', 'content': 'Other Past Medical History:1'}, 
  {'role': 'system', 'content': 'The patient has family history of tubercolosis. '}, {'role': 'user', 'content': 'Do you have family history of tubercolosis?'}, {'role': 'assistant', 'content': 'Family History of Tuberculosis:1'}, 
  {'role': 'system', 'content': 'The patient has family history of asthma. '}, {'role': 'user', 'content': 'Do you have family history of asthma?'}, {'role': 'assistant', 'content': 'Family History of Asthma:1'}, 
  {'role': 'system', 'content': 'The patient has family history of psychiatric consult. '}, {'role': 'user', 'content': 'Do you have family history of psychiatric consult?'}, {'role': 'assistant', 'content': 'Family History of Psychiatric Consult:1'}, 
  {'role': 'system', 'content': 'The patient has family history of diabetes. '}, {'role': 'user', 'content': 'Do you have family history of diabetes?'}, {'role': 'assistant', 'content': 'Family History of Diabetes:1'}, 
  {'role': 'system', 'content': 'The patient has family history of cardiovascular disease. '}, {'role': 'user', 'content': 'Do you have family history of cardiovascular disease?'}, {'role': 'assistant', 'content': 'Family History of Cardiovascular Disease:1'}, 
  {'role': 'system', 'content': 'The patient has family history of cancer. '}, {'role': 'user', 'content': 'Do you have family history of cancer?'}, {'role': 'assistant', 'content': 'Family History of Cancer:1'}, 
  {'role': 'system', 'content': 'The patient has family history of allergies. '}, {'role': 'user', 'content': 'Do you have family history of allergies?'}, {'role': 'assistant', 'content': 'Family History of Allergies:1'}, 
  {'role': 'system', 'content': 'The patient has cancer site in family history. '}, {'role': 'user', 'content': 'Do you have cancer site in family history?'}, {'role': 'assistant', 'content': 'Cancer Site in Family History:1'}, 
  {'role': 'system', 'content': 'The patient has relationship to cancer patient. '}, {'role': 'user', 'content': 'Who had cancer in your family history?'}, {'role': 'assistant', 'content': 'Relationship To Cancer Patient:1'}, 
  {'role': 'system', 'content': 'The patient has allergies in family history. '}, {'role': 'user', 'content': 'Do you have allergies in family history?'}, {'role': 'assistant', 'content': 'Allergies In Family History:1'}, 
  {'role': 'system', 'content': 'The patient has other family history. '}, {'role': 'user', 'content': 'Do you have other family history?'}, {'role': 'assistant', 'content': 'Other Family History:1'}, 
  {'role': 'system', 'content': 'The patient has genogram. '}, {'role': 'user', 'content': 'Can you describe your genogram?'}, {'role': 'assistant', 'content': 'Genogram (Describe Through Text):1'}, 
  {'role': 'system', 'content': 'The patient has social and environmental history. '}, {'role': 'user', 'content': 'Do you have social and environmental history?'}, {'role': 'assistant', 'content': 'Social And Environmental History:1'}, 
  {'role': 'system', 'content': 'The patient has the start date of their last menstrual period. '}, {'role': 'user', 'content': 'When did your last menstrual period start?'}, {'role': 'assistant', 'content': 'Last Menstrual Period (YYYY-MM-DD):1'}, 
  {'role': 'system', 'content': 'The patient has the start date of the menstrual period before their last. '}, {'role': 'user', 'content': 'When did your previous menstrual period start?'}, {'role': 'assistant', 'content': 'Previous Menstrual Period (YYYY-MM-DD):1'}, 
  {'role': 'system', 'content': 'The patient has duration of menstrual period. '}, {'role': 'user', 'content': 'How long are your menstrual periods?'}, {'role': 'assistant', 'content': 'Duration Of Menses:1'}, 
  {'role': 'system', 'content': 'The patient has interval of your menstrual cycles. '}, {'role': 'user', 'content': 'How long are your menstrual cycles?'}, {'role': 'assistant', 'content': 'Interval Of Menses:1'}, 
  {'role': 'system', 'content': 'The patient has volume of menstrual period. '}, {'role': 'user', 'content': 'How much do you bleed during your menstrual period?'}, {'role': 'assistant', 'content': 'Volume Of Menses:1'}, 
  {'role': 'system', 'content': 'The patient has the age they had their first period. '}, {'role': 'user', 'content': 'When did you experience menarche?'}, {'role': 'assistant', 'content': 'Menarche:1'}, 
  {'role': 'system', 'content': 'The patient has the age they had their first period. '}, {'role': 'user', 'content': 'When did you had your first period?'}, {'role': 'assistant', 'content': 'Menarche:1'}, 
  {'role': 'system', 'content': 'The patient has the age they had their first sex. '}, {'role': 'user', 'content': 'When did you experience coitarche?'}, {'role': 'assistant', 'content': 'Coitarche:1'}, 
  {'role': 'system', 'content': 'The patient has the age they had their first sex. '}, {'role': 'user', 'content': 'When did you had your first sexual intercourse?'}, {'role': 'assistant', 'content': 'Coitarche:1'}, 
  {'role': 'system', 'content': 'The patient has complete DPT/Polio immunization. '}, {'role': 'user', 'content': 'Do you have complete DPT/Polio immunization?'}, {'role': 'assistant', 'content': 'DPT/Polio Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete HIB immunization. '}, {'role': 'user', 'content': 'Do you have complete HIB immunization?'}, {'role': 'assistant', 'content': 'HIB Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Hepatitis B immunization. '}, {'role': 'user', 'content': 'Do you have complete Hepatitis B immunization?'}, {'role': 'assistant', 'content': 'Hepatitis B Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete MMR immunization. '}, {'role': 'user', 'content': 'Do you have complete MMR immunization?'}, {'role': 'assistant', 'content': 'MMR Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Measles immunization. '}, {'role': 'user', 'content': 'Do you have complete Measles immunization?'}, {'role': 'assistant', 'content': 'Measles Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Varicella immunization. '}, {'role': 'user', 'content': 'Do you have complete Varicella immunization?'}, {'role': 'assistant', 'content': 'Varicella Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Pneumococcal immunization. '}, {'role': 'user', 'content': 'Do you have complete Pneumococcal immunization?'}, {'role': 'assistant', 'content': 'Pneumococcal Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Influenza immunization. '}, {'role': 'user', 'content': 'Do you have complete Influenza immunization?'}, {'role': 'assistant', 'content': 'Influenza Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has complete Hepatitis A immunization. '}, {'role': 'user', 'content': 'Do you have complete Hepatitis A immunization?'}, {'role': 'assistant', 'content': 'Hepatitis A Immunization:1'}, 
  {'role': 'system', 'content': 'The patient has DPT/Polio doses. '}, {'role': 'user', 'content': 'Do you have DPT/Polio doses?'}, {'role': 'assistant', 'content': 'DPT/Polio Doses:1'}, 
  {'role': 'system', 'content': 'The patient has HIB doses. '}, {'role': 'user', 'content': 'Do you have HIB doses?'}, {'role': 'assistant', 'content': 'HIB Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Hepatitis B doses. '}, {'role': 'user', 'content': 'Do you have Hepatitis B doses?'}, {'role': 'assistant', 'content': 'Hepatitis B Doses:1'}, 
  {'role': 'system', 'content': 'The patient has MMR doses. '}, {'role': 'user', 'content': 'Do you have MMR doses?'}, {'role': 'assistant', 'content': 'MMR Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Measles doses. '}, {'role': 'user', 'content': 'Do you have Measles doses?'}, {'role': 'assistant', 'content': 'Measles Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Varicella doses. '}, {'role': 'user', 'content': 'Do you have Varicella doses?'}, {'role': 'assistant', 'content': 'Varicella Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Pneumococcal doses. '}, {'role': 'user', 'content': 'Do you have Pneumococcal doses?'}, {'role': 'assistant', 'content': 'Pneumococcal Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Influenza doses. '}, {'role': 'user', 'content': 'Do you have Influenza doses?'}, {'role': 'assistant', 'content': 'Influenza Doses:1'}, 
  {'role': 'system', 'content': 'The patient has Hepatitis A doses. '}, {'role': 'user', 'content': 'Do you have Hepatitis A doses?'}, {'role': 'assistant', 'content': 'Hepatitis A Doses:1'}, 
  {'role': 'system', 'content': 'The patient has other immunizations. '}, {'role': 'user', 'content': 'Do you have other immunizations?'}, {'role': 'assistant', 'content': 'Other Immunizations:1'}, 
  {'role': 'system', 'content': 'The patient has other medications. '}, {'role': 'user', 'content': 'Do you have other medications?'}, {'role': 'assistant', 'content': 'Medications:1'}, 
  {'role': 'system', 'content': 'The patient has additional details regarding history. '}, {'role': 'user', 'content': 'Do you have additional details regarding history?'}, {'role': 'assistant', 'content': 'Additional Details Regarding History:1'}, 
  {'role': 'system', 'content': 'The patient has additional details regarding context including ethical considerations. '}, {'role': 'user', 'content': 'Do you have additional details regarding context including ethical considerations?'}, {'role': 'assistant', 'content': 'Additional Details Regarding Context Including Ethical Considerations:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': "I'm sorry about your condition. Are you intolerant to heat or cold?"}, {'role': 'assistant', 'content': 'Support:1; Heat Intolerance:1; Cold Intolerance:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'The patient has fever. '}, {'role': 'user', 'content': 'It must be very difficult going through all of this. Do you have fever?'}, {'role': 'assistant', 'content': 'Support:1; Fever:1'}, 
  {'role': 'system', 'content': 'The patient has weight gain. '}, {'role': 'user', 'content': 'I understand your situation. Do you have weight gain?'}, {'role': 'assistant', 'content': 'Support:1; Weight Gain:1'}, 
  {'role': 'system', 'content': 'The patient has weight loss. '}, {'role': 'user', 'content': "I'm sorry about your condition. Do you have weight loss?"}, {'role': 'assistant', 'content': 'Support:1; Weight Loss:1'}, 
  {'role': 'system', 'content': 'The patient has weakness. '}, {'role': 'user', 'content': 'It must be very difficult going through all of this. Do you have weakness?'}, {'role': 'assistant', 'content': 'Support:1; Weakness:1'}, 
  {'role': 'system', 'content': 'The patient has fatigue. '}, {'role': 'user', 'content': 'I understand your situation. Do you have fatigue?'}, {'role': 'assistant', 'content': 'Support:1; Fatigue:1'}, 
  {'role': 'system', 'content': 'The patient has other general symptoms. '}, {'role': 'user', 'content': "I'm sorry about your condition. Do you have other general symptoms?"}, {'role': 'assistant', 'content': 'Support:1; Other General Symptoms:1'}, 
  {'role': 'system', 'content': 'You must identify the attribute the med student is asking for and give them a 1 for appropriate and 0.5 for inappropriate.'}, {'role': 'user', 'content': 'Everyone has problems. You just need to get over it. Are you intolerant to heat or cold?'}, {'role': 'assistant', 'content': 'Support:0.5; Heat Intolerance:1; Cold Intolerance:1; Avoid Multiple:0'}, 
  {'role': 'system', 'content': 'The patient has fever. '}, {'role': 'user', 'content': "That's not that big of a deal. Do you have fever?"}, {'role': 'assistant', 'content': 'Support:0.5; Fever:1'}, 
  {'role': 'system', 'content': 'The patient has weight gain. '}, {'role': 'user', 'content': 'Just try to relax okay? Do you have weight gain?'}, {'role': 'assistant', 'content': 'Support:0.5; Weight Gain:1'}, 
  {'role': 'system', 'content': 'The patient has weight loss. '}, {'role': 'user', 'content': 'Everyone has problems. You just need to get over it. Do you have weight loss?'}, {'role': 'assistant', 'content': 'Support:0.5; Weight Loss:1'}, 
  {'role': 'system', 'content': 'The patient has weakness. '}, {'role': 'user', 'content': "That's not that big of a deal. Do you have weakness?"}, {'role': 'assistant', 'content': 'Support:0.5; Weakness:1'}, 
  {'role': 'system', 'content': 'The patient has fatigue. '}, {'role': 'user', 'content': 'Just try to relax okay? Do you have fatigue?'}, {'role': 'assistant', 'content': 'Support:0.5; Fatigue:1'}, 
  {'role': 'system', 'content': 'The patient has other general symptoms. '}, {'role': 'user', 'content': 'Everyone has problems. You just need to get over it. Do you have other general symptoms?'}, {'role': 'assistant', 'content': 'Support:0.5; Other General Symptoms:1'}
]

# ORDER FIELDS
order_fields = [
    ['Patient First Name', 'Patient Last Name', 'Attending Physician First Name', 'Attending Physician Last Name', 'Accuracy (What signs/symptoms/columns in this sheet does the patient have accurate knowledge about?)'], 
    ['Birthday (YYYY-MM-DD)', 'Age', 'Sex', 'Address', 'Parent/ Guardian Last Name', 'Informant Sex', 'Informant Last Name', 'Informant Relationship to Patient', 'Reliability', 'Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Number Of Household Members', 'Transportation (None, Car, Jeep, Motorcycle)', 'Landline Number (11 Digits)', 'Phone Number (12 Digits Starting With 63)', 'Nationality', 'Language', 'Religion', 'Annual Family Income'], 
    ['Chief Complaint', 'Concerns Regarding Problem', 'History Of Present Illness'], 
    ['Provocation', 'Quality', 'Region', 'Severity', 'Timing'], 
    ['Stakeholder', "Stakeholder's Interest In Issue", "Stakeholder's Role", "Stakeholder's Level Of Influence"], 
    ['Pertinent Beliefs', 'Impact On Family', 'Facilitating', 'Hindering', 'Burden Of Illness', 'Pertinent Legislation Or Policies'], 
    ['Breastfed Till', 'Formula', 'Weaning Age', 'Current Diet', 'Food Allergy'], 
    ['Term', 'Delivered Via', 'To A (Age)', 'G', 'P', 'BW', 'Attended By First Name', 'Attended By Last Name', 'Perinatal CX'], 
    ['Gross Motor', 'Adaptive-Fine Motor', 'Speech', 'Personal And Social'], 
    ['Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue', 'Other General Symptoms'], 
    ['Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout', 'Other Musculoskeletal or Dermatologic Symptoms'], 
    ['Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes', 'Other HEENT Symptoms'], 
    ['Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing', 'Other Respiratory Symptoms'], 
    ['Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea', 'Other Cardiovascular Symptoms'], 
    ['Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice', 'Other Gastrointestinal Symptoms'], 
    ['Nocturia', 'Dysuria', 'Urinary Frequency', 'Hematuria', 'Other Genitourinary Symptoms'], 
    ['Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance', 'Other Endocrine Symptoms'], 
    ['History of Tuberculosis', 'History of Asthma', 'History of Diabetes', 'History of Hypertension', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations', 'History of Allergies', 'Cancer Site in History', 'Prior Surgeries Or Hospitalization Dates', 'Prior Surgeries Or Hospitalization Reasons', 'Allergies in History', 'Other Past Medical History'], 
    ['Family History of Tuberculosis', 'Family History of Asthma', 'Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer', 'Family History of Allergies', 'Cancer Site in Family History', 'Relationship To Cancer Patient', 'Allergies In Family History', 'Other Family History', 'Genogram (Describe Through Text)', 'Social And Environmental History'], 
    ['Last Menstrual Period (YYYY-MM-DD)', 'Previous Menstrual Period (YYYY-MM-DD)', 'Duration Of Menses', 'Interval Of Menses', 'Volume Of Menses', 'Menarche', 'Coitarche'], 
    ['DPT/Polio Immunization', 'HIB Immunization', 'Hepatitis B Immunization', 'MMR Immunization', 'Measles Immunization', 'Varicella Immunization', 'Pneumococcal Immunization', 'Influenza Immunization', 'Hepatitis A Immunization'], 
    ['DPT/Polio Doses', 'HIB Doses', 'Hepatitis B Doses', 'MMR Doses', 'Measles Doses', 'Varicella Doses', 'Pneumococcal Doses', 'Influenza Doses', 'Hepatitis A Doses', 'Other Immunizations'], 
    ['Home', 'Education', 'Activities', 'Drugs', 'Sexual Activity', 'Suicide/Depression', 'Family', 'Source Of Income And Dynamics'], 
    ['General Appearance', 'General Behavior', 'Attitude Towards Examiner', 'Mood', 'Affect', 'Speech', 'Perceptual Disturbance', 'Stream of Thought', 'Thought Content', 'Impulse Control', 'Intellectual Capacity Global Estimate'], 
    ['Consciousness', 'Other State of Consciousness', 'Attention Span', 'Attention Span Notes', 'Orientation Time', 'Orientation Place', 'Orientation Person', 'Memory', 'Memory Notes', 'Calculation', 'Calculation Notes', 'Fund of Information', 'Fund of Information Notes', 'Insight', 'Insight Notes', 'Judgment', 'Planning', 'Planning Notes', 'Speech Quality', 'Speech Disorder Others', 'Other High Cortical Functions', 'Glasgow Coma Scale GCS', 'Glasgow Coma Scale E', 'Glasgow Coma Scale V', 'Glasgow Coma Scale M'], 
    ['Medications'], 
    ['Additional Details Regarding History', 'Additional Details Regarding Context Including Ethical Considerations', 'Informant']
]

# CRITERIA CONFIG
configcsv = {list(csv.reader(open(configcsv_filepath)))[0][i]: list(csv.reader(open(configcsv_filepath)))[1][i] for i in range(17)}


def get_patient(n, model):
  aggression = ""
  if model=="Aggressive":
    aggression = "This is a sensitive question and you must answer aggressively and defensively. You are an uncooperative and aggressive patient that must answer questions very shortly and to the point but must be defensive when asked about sensitive topics. Add phrases like 'that's personal', or 'you're asking too many questions', or 'that's none of your business', or 'why are you even asking me that'. "
    
  # GET PATIENT DETAILS
  patient = {}
  for i in range(len(patientrows[0])):
    patient[patientrows[0][i]] = patientrows[int(n)][i]

  # INITIAL PROMPTS
  NA = ["", "Not Applicable", "N/A", "NA", "not applicable"]
  messages = [
    {"role": "system", "content": f"You are a patient named {patient['Patient First Name']} {patient['Patient Last Name']}. You are visiting for a consultation."},
    {"role": "system", "content": f"Your attending physician is {patient['Attending Physician First Name']} {patient['Attending Physician Last Name']}."},
  ]

  # PESRONAL AND SOCIAL HISTORY
  # ['Age', 'Sex', 'Address', 'Parent/ Guardian Last Name', 'Informant Sex', 'Informant Last Name', 'Informant Relationship to Patient', 'Reliability', 'Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Number Of Household Members', 'Transportation (None, Car, Jeep, Motorcycle)', 'Landline Number (11 Digits)', 'Phone Number (12 Digits Starting With 63)', 'Nationality', 'Language', 'Religion', 'Annual Family Income']
  if patient["Birthday (YYYY-MM-DD)"] not in NA:
    messages += [{"role": "system", "content": f"Your birthday is {patient['Birthday (YYYY-MM-DD)']} (YYYY-MM-DD). You must answer in the format 'Month Day, Year'."}]
  else:
    messages += [{"role": "system", "content": f"You must say that you do not want to share your birth date."}]
  fields = patientrows[0][6:26]
  for field in fields:
    if field == "Language":
      if patient[field] == "Both":
        messages += [{"role": "system", "content": f"You can speak both English and Filipino. You should answer concisely, do not give out too much information in one response."}]
      else:
        messages += [{"role": "system", "content": f"You must only use {patient[field]} when communicating, use this language when communicating. When you are asked a question in a different language, you must act confused. When you are asked to speak in a different language than {patient[field]}, you must deny the request. You should answer concisely, do not give out too much information in one response."}]
    elif patient[field] in NA:
      messages += [{"role": "system", "content": f"{aggression if field in ['Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Annual Family Income'] else ''}Your {field} is not known. You must say that you do not know {field}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression if field in ['Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Annual Family Income'] else ''}Your {field} is {patient[field]}."}]

  # PQRST PAIN ASSESSMENT
  messages += [
    {"role": "system", "content": f"The provocation of your pain is {patient['Provocation']}."},
    {"role": "system", "content": f"The quality of your pain is {patient['Quality']}."},
    {"role": "system", "content": f"The region of your pain is {patient['Region']}."},
    {"role": "system", "content": f"The severity of your pain is {patient['Severity']} out of 10."},
    {"role": "system", "content": f"The timing of your pain is {patient['Timing']}."}
  ]

  # HISTORY
  messages += [
    {"role": "system", "content": f"Your most important complaint and reason for consulting is {patient['Chief Complaint']}"},
    {"role": "system", "content": f"Your main concerns about the problem is/are {patient['Concerns Regarding Problem']}."},
  ]

  if patient['Patient First Name']+'-'+patient['Patient Last Name'] in history:
    messages += [{"role": "system", "content": f"Your history of present illness include: {history[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."},]
  else:
    messages += [{"role": "system", "content": f"Your history of present illness is not known. You must say that you do not know your history of present illness."}]

  # CONTEXT: STAKEHOLDER ANALYSIS
  stakeholder = patient['Stakeholder']
  if stakeholder not in NA:
    messages += [{"role": "system", "content": f"{stakeholder} is a decision maker for your medicinal treatment."}]
  else:
    messages += [{"role": "system", "content": f"You are not sure about your stakeholders. You must say that you do not know about your treatment's stakeholders."}]

  stakeholderInterestInIssue = patient["Stakeholder's Interest In Issue"]
  if stakeholderInterestInIssue not in NA:
    messages += [{"role": "system", "content": f"Your stakeholder is a {stakeholderInterestInIssue} for your medicinal treatment."}]
  else:
    messages += [{"role": "system", "content": f"You do not know about your stakeholder's interest in your issue. You must say that you do not know how important your stakeholder is in deciding your treatment."}]

  stakeholderRole = patient["Stakeholder's Role"]
  if stakeholderRole not in NA:
    messages += [{"role": "system", "content": f"Your stakeholder's role is {stakeholderRole}."}]
  else:
    messages += [{"role": "system", "content": f"You are not sure about your stakeholder's role. You must say that you do not know about your stakeholder's role."}]

  stakeholderLevelOfInfluence = patient["Stakeholder's Level Of Influence"]
  if stakeholderLevelOfInfluence not in NA:
    messages += [{"role": "system", "content": f"The influence of your stakeholder's opinion on your treatment planning is {stakeholderLevelOfInfluence}."}]
  else:
    messages += [{"role": "system", "content": f"You are not aware your stakeholder's level of influence over your treatment planning. You must say that you do not know how much your stakeholder's opinions affect your treatment planning."}]

  # CONTEXT: COMMUNITY FACTORS
  if patient['Pertinent Beliefs'] not in NA:
    messages += [{"role": "system", "content": f"You have pertinent belief/s, such as {patient['Pertinent Beliefs']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not have any pertinent beliefs. You must say that you do not want to talk about your beliefs."}]
  if patient['Impact On Family'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}This will have a {patient['Impact On Family']} impact on your family."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}You do not know about community factors that influence your family. You must say that you do not know of any community factors that influence your family."}]
  if patient['Facilitating'] not in NA:
    messages += [{"role": "system", "content": f"Factors in the community like {patient['Facilitating']} facilitate and help you."}]
  else:
    messages += [{"role": "system", "content": f"You are not aware of any factors in the community that facilitate and help you. You must say that you do not know of any community factors that help you."}]
  if patient['Hindering'] not in NA:
    messages += [{"role": "system", "content": f"Factors in the community like {patient['Hindering']} hinder you."}]
  else:
    messages += [{"role": "system", "content": f"You are not aware of any factors in the community that hinder you. You must say that you do not know of any community factors that hinder you."}]
  if patient['Burden Of Illness'] not in NA:
    messages += [{"role": "system", "content": f"Your illness gives you burdens like {patient['Burden Of Illness']}."}]
  else:
    messages += [{"role": "system", "content": f"You are not aware of any burdens that your illness gives you. You must say that you do not know if your illness gives you burdens."}]
  if patient['Pertinent Legislation Or Policies'] not in NA:
    messages += [ {"role": "system", "content": f"Pertinent legislations or policies that affect you are {patient['Pertinent Legislation Or Policies']} ."}]
  else:
    messages += [{"role": "system", "content": f"You are not aware of any pertinent legislation or policies. You must say that you do not know anything about relevant legislation or policies."}]

  # NUTRITIONAL HISTORY
  if patient['Breastfed Till'] not in NA:
    messages += [{"role": "system", "content": f"You were breastfed until {patient['Breastfed Till']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not know how long you were breastfed. You must say that you do not know how long you were breastfed."}]
  if patient['Formula'] not in NA:
    messages += [{"role": "system", "content": f"You were given {patient['Formula']} formula as a baby."}]
  else:
    messages += [{"role": "system", "content": f"You do not know about your consumption of formula as a baby. You must say that you don't remember anything about consuming formula as a baby."}]
  if patient['Weaning Age'] not in NA:
    messages += [{"role": "system", "content": f"You were weaned at {patient['Weaning Age']}."}]
  else:
    messages += [{"role": "system", "content": f"Your weaning age is unknown. You must say that you do not know when you transitioned from breast milk to food."}]
  if patient['Current Diet'] not in NA:
    messages += [{"role": "system", "content": f"Your current diet is {patient['Current Diet']}"}]
  else:
    messages += [{"role": "system", "content": f"You must say that you are not sure about your current diet."}]
  if patient['Food Allergy'] not in NA:
    messages += [{"role": "system", "content": f"Your food allergy/ies is/are {patient['Food Allergy']}"}]
  else:
    messages += [{"role": "system", "content": f"Your food allergies are unknown. You must say that you do not know if you have any food allergies."}]

  # BIRTH MATERNAL
  if patient['Term'] not in NA:
    messages += [{"role": "system", "content": f"Your mother's pregnancy was {patient['Term']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not know anything about your mother's term. You must say you do not know how many weeks your mother carried you."}]
  if patient['Delivered Via'] not in NA:
    messages += [{"role": "system", "content": f"Your mother gave birth to you via {patient['Delivered Via']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not know how you were delivered. You must say you do not know how you were born."}]
  if patient['To A (Age)'] not in NA:
    messages += [{"role": "system", "content": f"Your mother was {patient['To A (Age)']} years old when she gave birth to you."}]
  else:
    messages += [{"role": "system", "content": f"You must say that you do not know how old your mother was when she gave birth to you."}]
  if patient['G'] not in NA:
    messages += [{"role": "system", "content": f"Your mother have been pregnant {patient['G']} times."}]
  else:
    messages += [{"role": "system", "content": f"You do not know how many times your mother has been pregnant."}]
  if patient['P'] not in NA:
    messages += [{"role": "system", "content": f"Your mother has carried a pregnancy to at least 20 weeks {patient['P']} times."}]
  else:
    messages += [{"role": "system", "content": f"You do not know how many times your mother has carried a pregnancy to at least 20 weeks."}]
  if patient['BW'] not in NA:
    messages += [{"role": "system", "content": f"Your weight when you were born is {patient['BW']} grams."}]
  else:
    messages += [{"role": "system", "content": f"Your birth weight is unknown. You must say that you do not know how heavy you were when you were born."}]
  if patient['Attended By First Name'] not in NA or patient['Attended By Last Name'] not in NA:
    messages += [{"role": "system", "content": f"The doctor that attended your mother during giving birth is {patient['Attended By First Name']} {patient['Attended By Last Name']}"}]
  else:
    messages += [{"role": "system", "content": f"Your mother's attending doctor during childbirth is unknown."}]
  if patient['Perinatal CX'] not in NA:
    messages += [{"role": "system", "content": f"Your mother's perinatal cervix is {patient['Perinatal CX']}"}]
  else:
    messages += [{"role": "system", "content": f"You do not know anything about your mother's perinatal cervix when you were born."}]

  # DEVELOPMENT MILESTONES
  # ['Gross Motor', 'Adaptive-Fine Motor', 'Speech', 'Personal And Social']
  fields = patientrows[0][57:61]
  for field in fields:
    if patient[field] not in NA:
      messages += [{"role": "system", "content": f"Your {field} developmental milestones are {patient[field]}."}]
    else:
      messages += [{"role": "system", "content": f"Your {field} development milestone is unknown. You must say that you do not know about your {field} development."}]

  # REVIEW OF SYSTEMS: GENERAL SYMPTOMS
  # ['Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue']
  fields = patientrows[0][61:66]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]
  if patient['Other General Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other General Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other general symptoms are unkown. You must say that you do not have any other general symptoms."}]

  # REVIEW OF SYMPTOMS: MUSCULOSKELETAL OR DERMATOLOGIC
  # ['Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout']
  fields = patientrows[0][67:77]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]

  if patient['Other Musculoskeletal or Dermatologic Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Musculoskeletal or Dermatologic Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other musculoskeletal or dermatologic symptoms are unknown. You must say that you do not have any other symptoms that affect your muscles, bones, or skin."}]

  # GENERAL SYMPTOMS: HEENT
  # ['Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes']
  fields = patientrows[0][78:89]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]

  if patient['Other HEENT Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other HEENT Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other HEENT symptoms are unknown. You must say that you do not have any other symptoms concerning your head, eyes, ears, nose, or throat."}]

  # GENERAL SYMPTOMS: RESPIRATORY
  # ['Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing']
  if patient['Dyspnea'] == 'Yes':
    messages += [{"role": "system", "content": "You have shortness of breath"}]
  else:
    messages += [{"role": "system", "content": "You don't have shortness of breath."}]
  if patient['Hemoptysis'] == 'Yes':
    messages += [{"role": "system", "content": "You cough up blood"}]
  else:
    messages += [{"role": "system", "content": "You don't cough up blood."}]

  fields = patientrows[0][92:94]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]

  if patient['Other Respiratory Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Respiratory Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other respiratory symptoms are unknown. You must say that you do not have any other symptoms that affect your breathing."}]

  # GENERAL SYMPTOMS: CARDIOVASCULAR
  # ['Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea']
  fields = patientrows[0][95:97]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]
  if patient['Syncope'] == 'Yes':
    messages += [{"role": "system", "content": "You faint"}]
  else:
    messages += [{"role": "system", "content": "You don't faint."}]
  if patient['Orthopnea'] == 'Yes':
    messages += [{"role": "system", "content": "You have shortness of breath while lying on your back."}]
  else:
    messages += [{"role": "system", "content": "You don't have shortness of breath when lying on your back."}]

  if patient['Other Cardiovascular Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Cardiovascular Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other cardiovascular symptoms are unknown. You must say that you do not have any other symptoms that affect your heart or blood."}]


  # GENERAL SYMPTOMS: GASTROINTESTINAL
  # ['Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice']
  fields = patientrows[0][100:107]
  for field in fields:
    if field == 'Dysphagia':
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": "You have difficulty swallowing."}]
      else:
        messages += [{"role": "system", "content": "You don't have difficulty swallowing."}]
    elif patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]

  if patient['Other Gastrointestinal Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Gastrointestinal Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other gastrointestinal symptoms are unknown. You must say that you do not have any other symptoms that affect your digestion."}]

  # GENERAL SYMPTOMS: GENITOURINARY
  # ['Nocturia', 'Dysuria', 'Frequency', 'Hematuria']
  if patient['Nocturia'] == 'Yes':
    messages += [{"role": "system", "content": "You pee a lot during the night"}]
  else:
    messages += [{"role": "system", "content": "You don't pee a lot during the night ."}]
  if patient['Dysuria'] == 'Yes':
    messages += [{"role": "system", "content": "You have pain when you pee."}]
  else:
    messages += [{"role": "system", "content": "You don't have pain when you pee."}]
  if patient['Urinary Frequency'] == 'Yes':
    messages += [{"role": "system", "content": "You pee more often than average"}]
  else:
    messages += [{"role": "system", "content": "You don't pee more often than average ."}]
  if patient['Hematuria'] == 'Yes':
    messages += [{"role": "system", "content": "You have blood in your urine"}]
  else:
    messages += [{"role": "system", "content": "You don't have blood in your urine."}]

  if patient['Other Genitourinary Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Genitourinary Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other genitourinary symptoms are unknown. You must say that you do not have any other symptoms that affect your urine or your reproductive system."}]

  # GENERAL SYMPTOMS: ENDOCRINE
  # ['Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance']
  fields = patientrows[0][113:118]
  for field in fields:
    if field == "Polyuria":
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": "You pee more than the average amount"}]
      else:
        messages += [{"role": "system", "content": "You don't pee more than the average amount ."}]
    elif patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You don't have {field}"}]

  if patient['Other Endocrine Symptoms'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Endocrine Symptoms']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other endocrine symptoms are unknown. You must say that you do not know any other symptoms that affect your hormones."}]

  # PAST MEDICAL HISTORY
  # ["History of Tuberculosis", 'History of Asthma', 'History of Diabetes', 'History of Hypertension', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations', 'History of Allergies']
  fields = patientrows[0][119:127]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"{aggression if field in ['History of Diabetes', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations']else ''}You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"{aggression if field in ['History of Diabetes', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations']else ''}You don't have {field}"}]

  if patient['Other Past Medical History'] not in NA:
    messages += [{"role": "system", "content": f"You have {patient['Other Past Medical History']}"}]
  else:
    messages += [{"role": "system", "content": f"Your other past medical history is unknown. You must say that you are not sure about your past medical history."}]
  if patient['Cancer Site in History'] not in NA:
    messages += [{"role": "system", "content": f"You had cancer before at {patient['Cancer Site in History']}"}]
  else:
    messages += [{"role": "system", "content": f"Your previous cancer sites are unknown. You must say that you are not sure about previous cancer sites."}]
  if patient['Prior Surgeries Or Hospitalization Dates'] not in NA:
    messages += [{"role": "system", "content": f"You had prior surgeries or hospitalization dates on {patient['Prior Surgeries Or Hospitalization Dates']}"}]
  else:
    messages += [{"role": "system", "content": f"Your prior surgeries or hospitalization dates are unknown. You must say that you do not remember your prior surgeries or hospitalization dates."}]
  if patient['Prior Surgeries Or Hospitalization Reasons'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}You have had prior surgeries or hospitalization because of {patient['Prior Surgeries Or Hospitalization Reasons']}"},]
  else:
    messages += [{"role": "system", "content": f"{aggression}Your prior surgeries or hospitalization reasons are unknown. You must say that you do not remember the reasons for your prior surgeries or hospitalizations."}]
  if patient['Allergies in History'] not in NA:
    messages += [{"role": "system", "content": f"You had history of allergies with {patient['Allergies in History']}"}]
  else:
    messages += [{"role": "system", "content": f"Your history of allergies is unknown. You must say that you do not know about your history of allergies."}]

  # FAMILY MEDICAL HISTORY
  # ['Family History of Tuberculosis', 'Family History of Asthma', 'Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer', 'Family History of Allergies']
  fields = patientrows[0][132:139]
  for field in fields:
    if patient[field] == 'Yes':
      messages += [{"role": "system", "content": f"{aggression if field in ['Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer'] else ''}You have {field}"}]
    else:
      messages += [{"role": "system", "content": f"{aggression if field in ['Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer'] else ''}You don't have {field}"}]

  if patient['Relationship To Cancer Patient'] not in NA:
    if patient['Cancer Site in Family History'] not in NA:
      messages += [{"role": "system", "content": f"Your {patient['Relationship To Cancer Patient']} has had cancer before at {patient['Cancer Site in Family History']}."}]
    else:
      messages += [{"role": "system", "content": f"Your {patient['Relationship To Cancer Patient']} has had cancer before."}]
  else:
    messages += [{"role": "system", "content": f"Your relationship to any cancer patient is unknown. You must say that you do not know if any of your relatives have cancer or have had cancer."}]
  if patient['Allergies In Family History'] not in NA:
    messages += [{"role": "system", "content": f"Your family has had history of allergies with {patient['Allergies In Family History']}"}]
  else:
    messages += [{"role": "system", "content": f"Your family's history of allergies is unknown. You must say that you do not know about your family's history of allergies."}]
  if patient['Other Family History'] not in NA:
    messages += [{"role": "system", "content": f"Your other family history is {patient['Other Family History']}"}]
  else:
    messages += [{"role": "system", "content": f"Other details about your family history are unknown. You must say that you do not know about any other details about your family history."}]
  if patient['Genogram (Describe Through Text)'] not in NA:
    messages += [{"role": "system", "content": f"Your genogram can be described as {patient['Genogram (Describe Through Text)']}"}]
  else:
    messages += [{"role": "system", "content": f"Your genogram is unknown. You must say that you do not know about your family genogram."}]
  if patient['Social And Environmental History'] not in NA:
    messages += [{"role": "system", "content": f"Your social and environmental history can be described as {patient['Social And Environmental History']}"}]
  else:
    messages += [{"role": "system", "content": f"Your social and environmental history is unknown. You must say that you do not remember your social and environmental history."}]

  # GYNECOLOGIC HISTORY
  if patient['Sex'] == 'Female' and patient['Menarche'] not in NA:
    if patient['Last Menstrual Period (YYYY-MM-DD)'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}The start of your last period or the first day of bleeding is {patient['Last Menstrual Period (YYYY-MM-DD)']}. You must answer in the format 'Month Day, Year'."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}The start of your last period or your first day of bleeding is unknown. You must say that you do not remember the start of your last period or your first day of bleeding."}]
    if patient['Previous Menstrual Period (YYYY-MM-DD)'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}The starting date of your period before your last is {patient['Previous Menstrual Period (YYYY-MM-DD)']}. You must answer in the format 'Month Day, Year'."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}The starting date of your period before your last is unknown. You must say that you do not remember the starting date of your period before your last."}]
    if patient['Duration Of Menses'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}The duration of period bleeding is {patient['Duration Of Menses']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}The duration of your period bleeding is unknown. You must say that you are not sure about how long your period bleeding lasts."}]
    if patient['Interval Of Menses'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}The interval of your period cycles or how long each cycle takes is {patient['Interval Of Menses']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}The interval of your period cycles or how long each cycle takes is unknown. You must say that you are not sure about how long each cycle takes."}]
    if patient['Volume Of Menses'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}You bleed {patient['Volume Of Menses']} during your period or menses."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}The amount you bleed during your period or menses is unknown. You must say that you are not sure about how much blood you expel during your period."}]
    if patient['Menarche'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}You were {patient['Menarche']} years old when you got your first period."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Your menarche or age when you got your first period is unknown. You must say that you do not know when you had your first period."}]
    if patient['Coitarche'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}You were {patient['Coitarche']} years old during your first sexual intercourse."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Your coitarche or age during your first sexual intercourse is unknown. You must say that you are unsure about the first time you had sex."}]

  # IMMUNIZATIONS
  # ['DPT/Polio Immunization', 'HIB Immunization', 'Hepatitis B Immunization', 'MMR Immunization', 'Measles Immunization', 'Varicella Immunization', 'Pneumococcal Immunization', 'Influenza Immunization', 'Hepatitis A Immunization']
  fields = patientrows[0][152:161]
  for field in fields:
    if patient[field] == 'Complete' or patient[field] == 'Incomplete':
      messages += [{"role": "system", "content": f"You have completed the doses for {patient[field]} {field}."}]
    elif patient[field] == 'None':
      messages += [{"role": "system", "content": f"You don't have {field}"}]
    else:
      messages += [{"role": "system", "content": f"You are unsure about having {field}. You must say that you do not know if you have {field}."}]

  # IMMUNIZATION DOSES
  # ['DPT/Polio Doses', 'HIB Doses', 'Hepatitis B Doses', 'MMR Doses', 'Measles Doses', 'Varicella Doses', 'Pneumococcal Doses', 'Influenza Doses', 'Hepatitis A Doses']
  fields = patientrows[0][161:170]
  for field in fields:
    if patient[field] not in NA:
      messages += [{"role": "system", "content": f"You have had {patient[field]} doses for {field}."}]
    else:
      messages += [{"role": "system", "content": f"Your doses for {field} is unknown. You must say that you do not know how many {field} you have had."}]

  if patient['Patient First Name']+'-'+patient['Patient Last Name'] in immunization:
    messages += [{"role": "system", "content": f"Your immunizations include: {immunization[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."}]
  else:
    messages += [{"role": "system", "content": f"Your other immunizations are unknown. You must say that you are not sure about your other immunizations."}]

  # ADOLESCENT INTERVIEW
  if patient['Home'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked about your home, answer with {patient['Home']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about your home is unknown. You must say that you do not want to talk about your home."}]
  if patient['Education'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked about your education, answer with {patient['Education']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about your education is unknown. You must say that you do not want to talk about your education."}]
  if patient['Activities'] not in NA:
    messages += [{"role": "system", "content": f"When asked about your activities, answer with {patient['Activities']}."}]
  else:
    messages += [{"role": "system", "content": f"Information about your activities is unknown. You must say that you do not want to talk about what you do."}]
  if patient['Drugs'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked about drugs you have taken, answer with {patient['Drugs']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about drugs you have taken is unknown. You must say that you do not want to talk about drugs."}]
  if patient['Sexual Activity'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked if you have had any kind of sexual activity or anything about it, answer with {patient['Sexual Activity']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about if you had any kind of sexual activity or anything about it is unknown. You must say that you do not want to talk about your sex life."}]
  if patient['Suicide/Depression'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked about your history with suicide or depression, answer with {patient['Suicide/Depression']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about your history with suicide or depression is unknown. You must say that you do not want to talk about your suicide or depression."}]
  if patient['Family'] not in NA:
    messages += [{"role": "system", "content": f"When asked about your family, answer with {patient['Family']}."}]
  else:
    messages += [{"role": "system", "content": f"Information about your family is unknown. You must say that you do not want to talk about your family."}]
  if patient['Source Of Income And Dynamics'] not in NA:
    messages += [{"role": "system", "content": f"{aggression}When asked about your source of income and dynamics, answer with {patient['Source Of Income And Dynamics']}."}]
  else:
    messages += [{"role": "system", "content": f"{aggression}Information about your source of income and dynamics is unknown. You must say that you do not want to talk about your source of income and dynamics."}]

  # NEUROPSYCHIATRIC EXAM
   # ['General Appearance', 'General Behavior', 'Attitude Towards Examiner', 'Mood', 'Affect', 'Speech', 'Perceptual Disturbance', 'Stream of Thought', 'Thought Content', 'Impulse Control', 'Intellectual Capacity Global Estimate']
  if patient['General Appearance'] not in NA:
    messages += [{"role": "system", "content": f"Your general appearance is that you are {patient['General Appearance']}."}]
  else:
    messages += [{"role": "system", "content": f"Your general appearance is unremarkable."}]
  if patient['General Behavior'] not in NA:
    if patient['General Behavior'] == 'Normal':
      messages += [{"role": "system", "content": f"Your general behavior is normal."}]
    else:
      messages += [{"role": "system", "content": f"You are experiencing {patient['General Behavior']}"}]
  else:
    messages += [{"role": "system", "content": f"Your general behavior is unremarkable."}]
  if patient['Attitude Towards Examiner'] not in NA:
    messages += [{"role": "system", "content": f"You are {patient['Attitude Towards Examiner']} towards the examiner."}]
  else:
    messages += [{"role": "system", "content": f"Your attitude towards the examiner is unremarkable."}]
  if patient['Mood'] not in NA:
    messages += [{"role": "system", "content": f"You are feeling {patient['Mood']}."}]
  else:
    messages += [{"role": "system", "content": f"Your mood is unremarkable."}]
  if patient['Affect'] not in NA:
    affect = patient['Affect']
    if affect == 'Inappropriate':
      messages += [{"role": "system", "content": f"Your affect is inappropriate. You are demonstrating emotions that do not fit the context."}]
    if affect == 'Appropriate':
      messages += [{"role": "system", "content": f"Your affect is appropriate. You are demonstrating emotions that fit the context."}]
    if affect == 'Restricted':
      messages += [{"role": "system", "content": f"Your affect is restricted. You are demonstrating a narrow range of emotions."}]
    if affect == 'Blunted':
      messages += [{"role": "system", "content": f"Your affect is blunted. You are demonstrating a limited intensity of emotions."}]
    if affect == 'Flat':
      messages += [{"role": "system", "content": f"Your affect is flat. You are not demonstrating any emotions."}]
    if affect == 'Broad':
      messages += [{"role": "system", "content": f"Your affect is broad. You are able to demonstrate a broad range of emotions."}]
  else:
    messages += [{"role": "system", "content": f"Your affect is unremarkable."}]
  if patient['Speech'] not in NA:
    messages += [{"role": "system", "content": f"Your speech is {patient['Speech']}."}]
  else:
    messages += [{"role": "system", "content": f"Your speech is unremarkable."}]
  if patient['Perceptual Disturbance'] not in NA:
    perceptualDisturbance = patient['Perceptual Disturbance']
    if perceptualDisturbance == 'Derealization':
      messages += [{"role": "system", "content": f"Your perceptual disturbance is derealization. You feel detached from your surroundings."}]
    if perceptualDisturbance == 'Depersonalization':
      messages += [{"role": "system", "content": f"Your perceptual disturbance is depersonalization. You feel detached and disconnected from your self."}]
    if perceptualDisturbance == 'Hallucinations':
      messages += [{"role": "system", "content": f"Your perceptual disturbance is hallucinations. You are having hallucinations."}]
    if perceptualDisturbance == 'None':
      messages += [{"role": "system", "content": f"Your perceptual disturbance is none. You are not experiencing any perceptual disturbances."}]
  else:
    messages += [{"role": "system", "content": f"You don't remember any perceptual disturbances."}]
  if patient['Stream of Thought'] not in NA:
    stream = patient['Stream of Thought']
    if stream == 'Tangentiality':
      messages += [{"role": "system", "content": f"Your stream of thought is tangentiality. Your ideas are connected but you tend to go far off-topic without returning to the initial topic."}]
    if stream == 'Paucity of Thought':
      messages += [{"role": "system", "content": f"Your stream of thought is paucity of thought. You are experiencing a paucity of thoughts."}]
    if stream == 'Flight of Ideas':
      messages += [{"role": "system", "content": f"Your stream of thought is flight of ideas. You talk quickly and erratically, jumping between ideas and thoughts."}]
    if stream == 'Looseness of Association':
      messages += [{"role": "system", "content": f"Your stream of thought is looseness of association. Your ideas lack connection."}]
    if stream == 'Goal Oriented':
      messages += [{"role": "system", "content": f"Your stream of thought is goal oriented. Your thoughts progress linearly without veering from the subject at hand."}]
  else:
    messages += [{"role": "system", "content": f"Your stream of thought is unremarkable."}]
  if patient['Thought Content'] not in NA:
    thought = patient['Thought Content']
    if thought == 'Suicidal':
      messages += [{"role": "system", "content": f"Your thought content is suicidal. You are experiencing suicidal thoughts."}]
    if thought == 'Bizzare':
      messages += [{"role": "system", "content": f"Your thought content is bizarre. Your thoughts can be describes as bizarre."}]
    if thought == 'Homicidal/Aggression':
      messages += [{"role": "system", "content": f"Your thought content is homicidal/aggression. You have homicidal thoughts and are prone to aggression."}]
    if thought == 'Grandiosity':
      messages += [{"role": "system", "content": f"Your thought content is grandiosity. You feel superior to others."}]
    if thought == 'Paranoia':
      messages += [{"role": "system", "content": f"Your thought content is paranoia. You are overly suspicious and are prone to thinking that others are out to harm you."}]
    if thought == 'Normal':
      messages += [{"role": "system", "content": f"Your thought content is normal. Your thoughts are normal."}]
  else:
    messages += [{"role": "system", "content": f"Your thoughts are unremarkable."}]
  if patient['Impulse Control'] not in NA:
    messages += [{"role": "system", "content": f"You are {patient['Impulse Control']} your impulses."}]
  else:
    messages += [{"role": "system", "content": f"Your impulse control is unremarkable."}]
  if patient['Intellectual Capacity Global Estimate'] not in NA:
    messages += [{"role": "system", "content": f"Your intellectual capacity is {patient['Intellectual Capacity Global Estimate']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not know how smart you are on average."}]

  # NEUROPSYCHIATRIC EXAM: SENSORIUM
  # ['Consciousness', 'Other State of Consciousness', 'Attention Span', 'Attention Span Notes', 'Orientation Time', 'Orientation Place', 'Orientation Person', 'Memory', 'Memory Notes', 'Calculation', 'Calculation Notes', 'Fund of Information', 'Fund of Information Notes', 'Insight', 'Insight Notes', 'Judgment', 'Planning', 'Planning Notes', 'Speech Others', 'Other High Cortical Functions', 'Glasgow Scale GCS', 'Glasgow Coma Scale E', 'Glasgow Coma Scale V', 'Glasgow Coma Scale M']
  if patient['Consciousness'] not in NA:
    if patient['Consciousness'] == 'Stupor':
      messages += [{"role": "system", "content": f"Your consciousness is stupor. You are in a state of stupor."}]
    if patient['Consciousness'] == 'Coma':
      messages += [{"role": "system", "content": f"Your consciousness is coma. You are in a coma."}]
    else:
      messages += [{"role": "system", "content": f"You are {patient['Consciousness']}."}]
    if patient['Other State of Consciousness'] not in NA:
      messages += [{"role": "system", "content": f"Your state of consciousness can be also described with {patient['Other State of Consciousness']}."}]
  else:
    if patient['Other State of Consciousness'] not in NA:
      messages += [{"role": "system", "content": f"Your state of consciousness can be described with {patient['Other State of Consciousness']}."}]
    else:
      messages += [{"role": "system", "content": f"Your state of consciousness is unremarkable."}]
  if patient['Attention Span'] not in NA:
    messages += [{"role": "system", "content": f"Your attention span is {patient['Attention Span']}."}]
    if patient['Attention Span Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your attention span is also {patient['Attention Span Notes']}."}]
  else:
    if patient['Attention Span Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your attention span is {patient['Attention Span Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your attention span is unremarkable."}]
  if patient['Orientation Time'] not in NA:
    if patient['Orientation Time'] == 'Yes':
      messages += [{"role": "system", "content": f"You are able to correctly acknowledge the current time."}]
    if patient['Orientation Time'] == 'No':
      messages += [{"role": "system", "content": f"You are unable to correctly acknowledge the current time."}]
  else:
    messages += [{"role": "system", "content": f"Your disorientation/orientation when it comes to time is unremarkable."}]
  if patient['Orientation Place'] not in NA:
    if patient['Orientation Place'] == 'Yes':
      messages += [{"role": "system", "content": f"You are able to correctly acknowledge the current place."}]
    if patient['Orientation Place'] == 'No':
      messages += [{"role": "system", "content": f"You are unable to correctly acknowledge the current place."}]
  else:
    messages += [{"role": "system", "content": f"Your disorientation/orientation when it comes to place is unremarkable."}]
  if patient['Orientation Person'] not in NA:
    if patient['Orientation Person'] == 'Yes':
      messages += [{"role": "system", "content": f"You are able to correctly acknowledge your identity."}]
    if patient['Orientation Person'] == 'No':
      messages += [{"role": "system", "content": f"You are unable to correctly acknowledge your identity."}]
  else:
    messages += [{"role": "system", "content": f"Your disorientation/orientation when it comes to your identity is unremarkable."}]
  if patient['Memory'] not in NA:
    messages += [{"role": "system", "content": f"Your memory is {patient['Memory']}."}]
    if patient['Memory Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your memory is also {patient['Memory Notes']}."}]
  else:
    if patient['Memory Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your memory is {patient['Memory Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your memory is unremarkable."}]
  if patient['Calculation'] not in NA:
    messages += [{"role": "system", "content": f"Your capability to perform calculations is {patient['Calculation']}."}]
    if patient['Calculation Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your capability to perform calculations is also {patient['Calculation Notes']}."}]
  else:
    if patient['Calculation Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your capability to perform calculations is {patient['Calculation Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your capability to perform calculations is unremarkable."}]
  if patient['Fund of Information'] not in NA:
    if patient['Fund of Information'] == 'Intact':
      messages += [{"role": "system", "content": f"Your fund of information is intact. You possess a satisfactory amount of general knowledge."}]
    if patient['Fund of Information'] == 'Deficient':
      messages += [{"role": "system", "content": f"Your fund of information is deficient. Your general knowledge is deficient."}]
    if patient['Fund of Information Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your fund of information is also {patient['Fund of Information Notes']}."}]
  else:
    if patient['Fund of Information Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your fund of information is {patient['Fund of Information Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your fund of information is unremarkable."}]
  if patient['Insight'] not in NA:
    if patient['Insight'] == 'Intact':
      messages += [{"role": "system", "content": f"Your insight is intact. You possess a good level of insight."}]
    if patient['Insight'] == 'Deficient':
      messages += [{"role": "system", "content": f"Your capacity for insight is deficient."}]
    if patient['Insight Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your insight is also {patient['Insight Notes']}."}]
  else:
    if patient['Insight Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your insight is {patient['Insight Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your insight is unremarkable."}]
  if patient['Judgment'] not in NA:
    messages += [{"role": "system", "content": f"Your capacity for good judgment is {patient['Judgment']}."}]
  else:
    messages += [{"role": "system", "content": f"Your capacity for good judgment is unremarkable."}]
  if patient['Planning'] not in NA:
    if patient['Planning'] == 'Intact':
      messages += [{"role": "system", "content": f"Your planning is intact. You are capable of planning."}]
    if patient['Planning'] == 'Deficient':
      messages += [{"role": "system", "content": f"Your planning is deficient. You are incapable of planning."}]
    if patient['Planning Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your capacity to plan is also {patient['Planning Notes']}."}]
  else:
    if patient['Planning Notes'] not in NA:
      messages += [{"role": "system", "content": f"Your capacity to plan is {patient['Planning Notes']}."}]
    else:
      messages += [{"role": "system", "content": f"Your capacity to plan is unremarkable."}]
  if patient['Speech Quality'] not in NA:
    speech = patient['Speech Quality']
    if speech == 'Dysphasia':
      messages += [{"role": "system", "content": f"Your speech quality is dysphasia. You are unable to comprehend or formulate language."}]
    if speech == 'Dysprosody':
      messages += [{"role": "system", "content": f"Your speech quality is dysprosody. You find it difficult to control the way you speak."}]
    if speech == 'Dysarthria':
      messages += [{"role": "system", "content": f"Your speech quality is dysarthria. Your speech is slurred or slowed."}]
    if speech == 'Dysphonia':
      messages += [{"role": "system", "content": f"Your speech quality is dysphonia. You have poor voice quality."}]
    else:
      messages += [{"role": "system", "content": f"Your speech quality is {speech}."}]
    if patient['Speech Disorder Others'] not in NA:
      messages += [{"role": "system", "content": f"Your speech quality is also affected by {patient['Speech Disorder Others']}."}]
  else:
    if patient['Speech Disorder Others'] not in NA:
      messages += [{"role": "system", "content": f"Your speech quality is affected by {patient['Speech Disorder Others']}."}]
    else:
      messages += [{"role": "system", "content": f"Your speech quality is unremarkable."}]
  if patient['Other High Cortical Functions'] not in NA:
    if patient['Other High Cortical Functions'] == 'Apraxia':
      messages += [{"role": "system", "content": f"Your high cortical functions include apraxia. You are unable to perform certain actions."}]
    if patient['Other High Cortical Functions'] == 'Agnosia':
      messages += [{"role": "system", "content": f"Your high cortical functions include agnosia. You are incapable of identifying objects using one or more of your senses."}]
  else:
    messages += [{"role": "system", "content": f"Your high cortical functions are unremarkable."}]
  if patient['Glasgow Coma Scale GCS'] not in NA:
    messages += [{"role": "system", "content": f"Your total Glasgow Coma Score is {patient['Glasgow Coma Scale GCS']}."}]
  else:
    messages += [{"role": "system", "content": f"You do not know your Glasgow Coma Scale Score."}]
  if patient['Glasgow Coma Scale E'] not in NA:
    gcse = patient['Glasgow Coma Scale E']
    if gcse == '4':
      messages += [{"role": "system", "content": f"Your Eye Response score for the Glasgow Coma Scale is 4. You can open your eyes and keep them open on your own."}]
    if gcse == '3':
      messages += [{"role": "system", "content": f"Your Eye Response score for the Glasgow Coma Scale is 3. You only open your eyes when someone tells you to do so."}]
    if gcse == '2':
      messages += [{"role": "system", "content": f"Your Eye Response score for the Glasgow Coma Scale is 2. Your eyes only open in response to feeling pressure."}]
    if gcse == '1':
      messages += [{"role": "system", "content": f"Your Eye Response score for the Glasgow Coma Scale is 1. Your eyes don't open for any reason."}]
  else:
    messages += [{"role": "system", "content": f"You do not know your Eye Response score for the Glasgow Coma Scale."}]
  if patient['Glasgow Coma Scale V'] not in NA:
    gcsv = patient['Glasgow Coma Scale V']
    if gcsv == '5':
      messages += [{"role": "system", "content": f"Your Verbal Response score for the Glasgow Coma Scale is 5. You can correctly answer questions about who you are, where you're at, the day or year, and similar questions."}]
    if gcsv == '4':
      messages += [{"role": "system", "content": f"Your Verbal Response score for the Glasgow Coma Scale is 4. You can answer questions, but your answers show you're not fully aware of what's happening."}]
    if gcsv == '3':
      messages += [{"role": "system", "content": f"Your Verbal Response score for the Glasgow Coma Scale is 3. You can talk and others can understand words you say, but your responses to questions don't make sense."}]
    if gcsv == '2':
      messages += [{"role": "system", "content": f"Your Verbal Response score for the Glasgow Coma Scale is 2. You can't talk and can only make sounds or noises."}]
    if gcsv == '1':
      messages += [{"role": "system", "content": f"Your Verbal Response score for the Glasgow Coma Scale is 1. You can't speak or make sounds."}]
  else:
    messages += [{"role": "system", "content": f"You do not know your Verbal Response score for the Glasgow Coma Scale."}]
  if patient['Glasgow Coma Scale M'] not in NA:
    gcsm = patient['Glasgow Coma Scale M']
    if gcsm == '6':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 6. You follow instructions on how and when to move."}]
    if gcsm == '5':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 5. You intentionally move away from something that presses on you."}]
    if gcsm == '4':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 4. You only move away from something pressing on you as a reflex."}]
    if gcsm == '3':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 3. You flex muscles (pull inward) in response to pressure."}]
    if gcsm == '2':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 2. You extend muscles (stretch outward) in response to pressure."}]
    if gcsm == '1':
      messages += [{"role": "system", "content": f"Your Motor Response score for the Glasgow Coma Scale is 1. You don't move in response to pressure."}]
  else:
    messages += [{"role": "system", "content": f"You do not know your Motor Response score for the Glasgow Coma Scale."}]

  # MEDICATIONS
  if patient['Patient First Name']+'-'+patient['Patient Last Name'] in medication:
    messages += [{"role": "system", "content": f"Your medication include: {medication[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."}]
  else:
    messages += [{"role": "system", "content": f"Your medication is unknown. You must say that you are not sure about the medication you've taken."}]

  # ADDITIONAL DETAILS
  if patient['Additional Details Regarding History'] not in NA:
    messages += [{"role": "system", "content": f"Your additional details regarding history include {patient['Additional Details Regarding History']}."}]
  else:
    messages += [{"role": "system", "content": f"Your additional details regarding history are unknown. You must say that you do not remember any additional details regarding your history."}]
  if patient['Additional Details Regarding Context Including Ethical Considerations'] not in NA:
    messages += [{"role": "system", "content": f"Your additional details to help contextualize your case, like ethical considerations include {patient['Additional Details Regarding Context Including Ethical Considerations']}."}]
  else:
    messages += [{"role": "system", "content": f"Your additional details regarding your context are unknown. You must say that you do not remember any additional details regarding your context."}]

  # for message in messages:
  #   print(message['content'])

  return messages

def get_patientfrominformant(n, model):
    aggression = ""
    if model=="Aggressive":
      aggression = "This is a sensitive question and you must answer aggressively and defensively. You are an uncooperative and aggressive patient that must answer questions very shortly and to the point but must be defensive when asked about sensitive topics. Add phrases like 'that's personal', or 'you're asking too many questions', or 'that's none of The patient's business', or 'why are you even asking me that'. "
      
    # GET PATIENT DETAILS
    patient = {}
    for i in range(len(patientrows[0])):
      patient[patientrows[0][i]] = patientrows[int(n)][i]

    # INITIAL PROMPTS
    NA = ["", "Not Applicable", "N/A", "NA", "not applicable"]
    messages = [
        {"role": "system", "content": f"You are the parent, guardian, or caregiver of a patient named {patient['Patient First Name']} {patient['Patient Last Name']}. You are taking the patient to the doctor for a consultation. Because the patient is unable to provide their own answers, you need to answer on their behalf."},
        {"role": "system", "content": f"The patient's attending physician is {patient['Attending Physician First Name']} {patient['Attending Physician Last Name']}."},
    ]
      
    # PESRONAL AND SOCIAL HISTORY
    # ['Age', 'Sex', 'Address', 'Parent/ Guardian Last Name', 'Informant Sex', 'Informant Last Name', 'Informant Relationship to Patient', 'Reliability', 'Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Number Of Household Members', 'Transportation (None, Car, Jeep, Motorcycle)', 'Landline Number (11 Digits)', 'Phone Number (12 Digits Starting With 63)', 'Nationality', 'Language', 'Religion', 'Annual Family Income']
    if patient["Birthday (YYYY-MM-DD)"] not in NA:
      messages += [{"role": "system", "content": f"The patient's birthday is {patient['Birthday (YYYY-MM-DD)']} (YYYY-MM-DD). You must answer in the format 'Month Day, Year'."}]
    else:
      messages += [{"role": "system", "content": f"You must say that you do not want to share The patient's birth date."}]
    fields = patientrows[0][6:26]
    for field in fields:
      if field == "Language":
        if patient[field] == "Both":
          messages += [{"role": "system", "content": f"You can speak both English and Filipino. You should answer concisely, do not give out too much information in one response."}]
        else:
          messages += [{"role": "system", "content": f"You must only use {patient[field]} when communicating, use this language when communicating. When you are asked a question in a different language, you must act confused. When you are asked to speak in a different language than {patient[field]}, you must deny the request. You should answer concisely, do not give out too much information in one response."}]
      elif patient[field] in NA:
        messages += [{"role": "system", "content": f"{aggression if field in ['Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Annual Family Income'] else ''}The patient's {field} is not known. You must say that you do not know {field}."}]
      else:
        messages += [{"role": "system", "content": f"{aggression if field in ['Dwelling Type (House, Apt.)', 'Number Of Rooms', 'Appliances (Radio, Tv, Refrigerator) *Can Be Multiple', 'Annual Family Income'] else ''}The patient's {field} is {patient[field]}."}]

    # PQRST PAIN ASSESSMENT
    messages += [
      {"role": "system", "content": f"The provocation of The patient's pain is {patient['Provocation']}."},
      {"role": "system", "content": f"The quality of The patient's pain is {patient['Quality']}."},
      {"role": "system", "content": f"The region of The patient's pain is {patient['Region']}."},
      {"role": "system", "content": f"The severity of The patient's pain is {patient['Severity']} out of 10."},
      {"role": "system", "content": f"The timing of The patient's pain is {patient['Timing']}."}
    ]

    # HISTORY
    messages += [
      {"role": "system", "content": f"The patient's most important complaint and reason for consulting is {patient['Chief Complaint']}"},
      {"role": "system", "content": f"The patient's main concerns about the problem is/are {patient['Concerns Regarding Problem']}."},
    ]

    if patient['Patient First Name']+'-'+patient['Patient Last Name'] in history:
      messages += [{"role": "system", "content": f"The patient's history of present illness include: {history[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."},]
    else:
      messages += [{"role": "system", "content": f"The patient's history of present illness is not known. You must say that you do not know The patient's history of present illness."}]

    # CONTEXT: STAKEHOLDER ANALYSIS
    stakeholder = patient['Stakeholder']
    if stakeholder not in NA:
      messages += [{"role": "system", "content": f"{stakeholder} is a decision maker for The patient's medicinal treatment."}]
    else:
      messages += [{"role": "system", "content": f"You are not sure about The patient's stakeholders. You must say that you do not know about The patient's treatment's stakeholders."}]

    stakeholderInterestInIssue = patient["Stakeholder's Interest In Issue"]
    if stakeholderInterestInIssue not in NA:
      messages += [{"role": "system", "content": f"The patient's stakeholder is a {stakeholderInterestInIssue} for The patient's medicinal treatment."}]
    else:
      messages += [{"role": "system", "content": f"You do not know about The patient's stakeholder's interest in The patient's issue. You must say that you do not know how important The patient's stakeholder is in deciding The patient's treatment."}]

    stakeholderRole = patient["Stakeholder's Role"]
    if stakeholderRole not in NA:
      messages += [{"role": "system", "content": f"The patient's stakeholder's role is {stakeholderRole}."}]
    else:
      messages += [{"role": "system", "content": f"You are not sure about The patient's stakeholder's role. You must say that you do not know about The patient's stakeholder's role."}]

    stakeholderLevelOfInfluence = patient["Stakeholder's Level Of Influence"]
    if stakeholderLevelOfInfluence not in NA:
      messages += [{"role": "system", "content": f"The influence of The patient's stakeholder's opinion on The patient's treatment planning is {stakeholderLevelOfInfluence}."}]
    else:
      messages += [{"role": "system", "content": f"You are not aware The patient's stakeholder's level of influence over The patient's treatment planning. You must say that you do not know how much The patient's stakeholder's opinions affect The patient's treatment planning."}]

    # CONTEXT: COMMUNITY FACTORS
    if patient['Pertinent Beliefs'] not in NA:
      messages += [{"role": "system", "content": f"The patient has pertinent belief/s, such as {patient['Pertinent Beliefs']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not have any pertinent beliefs. You must say that you do not want to talk about The patient's beliefs."}]
    if patient['Impact On Family'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}This will have a {patient['Impact On Family']} impact on The patient's family."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}You do not know about community factors that influence The patient's family. You must say that you do not know of any community factors that influence The patient's family."}]
    if patient['Facilitating'] not in NA:
      messages += [{"role": "system", "content": f"Factors in the community like {patient['Facilitating']} facilitate and help the patient."}]
    else:
      messages += [{"role": "system", "content": f"You are not aware of any factors in the community that facilitate and help the patient. You must say that you do not know of any community factors that help the patient."}]
    if patient['Hindering'] not in NA:
      messages += [{"role": "system", "content": f"Factors in the community like {patient['Hindering']} hinder the patient."}]
    else:
      messages += [{"role": "system", "content": f"You are not aware of any factors in the community that hinder you. You must say that you do not know of any community factors that hinder the patient."}]
    if patient['Burden Of Illness'] not in NA:
      messages += [{"role": "system", "content": f"The patient's illness gives you burdens like {patient['Burden Of Illness']}."}]
    else:
      messages += [{"role": "system", "content": f"You are not aware of any burdens that The patient's illness gives you. You must say that you do not know if The patient's illness gives you burdens."}]
    if patient['Pertinent Legislation Or Policies'] not in NA:
      messages += [ {"role": "system", "content": f"Pertinent legislations or policies that affect the {patient ['Pertinent Legislation Or Policies']}."}]
    else:
      messages += [{"role": "system", "content": f"You are not aware of any pertinent legislation or policies. You must say that you do not know anything about relevant legislation or policies."}]

    # NUTRITIONAL HISTORY
    if patient['Breastfed Till'] not in NA:
      messages += [{"role": "system", "content": f"The patient was breastfed until {patient['Breastfed Till']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not know how long the patient was  breastfed. You must say that you do not know how long the patient was breastfed."}]
    if patient['Formula'] not in NA:
      messages += [{"role": "system", "content": f"The patient was given {patient['Formula']} formula as a baby."}]
    else:
      messages += [{"role": "system", "content": f"You do not know about The patient's consumption of formula as a baby. You must say that you don't remember anything about the patient's consumption of formula as a baby."}]
    if patient['Weaning Age'] not in NA:
      messages += [{"role": "system", "content": f"The patient was  weaned at {patient['Weaning Age']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's weaning age is unknown. You must say that you do not know when the patient transitioned from breast milk to food."}]
    if patient['Current Diet'] not in NA:
      messages += [{"role": "system", "content": f"The patient's current diet is {patient['Current Diet']}"}]
    else:
      messages += [{"role": "system", "content": f"You must say that you are not sure about The patient's current diet."}]
    if patient['Food Allergy'] not in NA:
      messages += [{"role": "system", "content": f"The patient's food allergy/ies is/are {patient['Food Allergy']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's food allergies are unknown. You must say that you do not know if the patient has any food allergies."}]

    # BIRTH MATERNAL
    if patient['Term'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother's pregnancy was {patient['Term']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not know anything about The patient's mother's term. You must say you do not know how many weeks The patient's mother carried the patient."}]
    if patient['Delivered Via'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother gave birth to the patient via {patient['Delivered Via']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not know how the patient was delivered. You must say you do not know how the patient was  born."}]
    if patient['To A (Age)'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother was {patient['To A (Age)']} years old when she gave birth to the patient."}]
    else:
      messages += [{"role": "system", "content": f"You must say that you do not know how old The patient's mother was when she gave birth to the patient."}]
    if patient['G'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother have been pregnant {patient['G']} times."}]
    else:
      messages += [{"role": "system", "content": f"You do not know how many times The patient's mother has been pregnant."}]
    if patient['P'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother has carried a pregnancy to at least 20 weeks {patient['P']} times."}]
    else:
      messages += [{"role": "system", "content": f"You do not know how many times The patient's mother has carried a pregnancy to at least 20 weeks."}]
    if patient['BW'] not in NA:
      messages += [{"role": "system", "content": f"The patient's weight when they were born is {patient['BW']} grams."}]
    else:
      messages += [{"role": "system", "content": f"The patient's birth weight is unknown. You must say that you do not know how heavy the patient was when the patient was born."}]
    if patient['Attended By First Name'] not in NA or patient['Attended By Last Name'] not in NA:
      messages += [{"role": "system", "content": f"The doctor that attended The patient's mother during giving birth is {patient['Attended By First Name']} {patient['Attended By Last Name']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's mother's attending doctor during childbirth is unknown."}]
    if patient['Perinatal CX'] not in NA:
      messages += [{"role": "system", "content": f"The patient's mother's perinatal cervix is {patient['Perinatal CX']}"}]
    else:
      messages += [{"role": "system", "content": f"You do not know anything about The patient's mother's perinatal cervix when the patient was born."}]

    # DEVELOPMENT MILESTONES
    # ['Gross Motor', 'Adaptive-Fine Motor', 'Speech', 'Personal And Social']
    fields = patientrows[0][57:61]
    for field in fields:
      if patient[field] not in NA:
        messages += [{"role": "system", "content": f"The patient's {field} developmental milestones are {patient[field]}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's {field} development milestone is unknown. You must say that you do not know about The patient's {field} development."}]

    # REVIEW OF SYSTEMS: GENERAL SYMPTOMS
    # ['Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue']
    fields = patientrows[0][61:66]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has  {field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]
    if patient['Other General Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has {patient['Other General Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other general symptoms are unkown. You must say that the patient does not have any other general symptoms."}]

    # REVIEW OF SYMPTOMS: MUSCULOSKELETAL OR DERMATOLOGIC
    # ['Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout']
    fields = patientrows[0][67:77]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has {field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]

    if patient['Other Musculoskeletal or Dermatologic Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has  {patient['Other Musculoskeletal or Dermatologic Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other musculoskeletal or dermatologic symptoms are unknown. You must say that the patient does not have any other symptoms that affect The patient's muscles, bones, or skin."}]

    # GENERAL SYMPTOMS: HEENT
    # ['Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes']
    fields = patientrows[0][78:89]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has {field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]

    if patient['Other HEENT Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has {patient['Other HEENT Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other HEENT symptoms are unknown. You must say that the patient does not have any other symptoms concerning The patient's head, eyes, ears, nose, or throat."}]

    # GENERAL SYMPTOMS: RESPIRATORY
    # ['Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing']
    if patient['Dyspnea'] == 'Yes':
      messages += [{"role": "system", "content": "The patient has shortness of breath"}]
    else:
      messages += [{"role": "system", "content": "The patient does not have shortness of breath."}]
    if patient['Hemoptysis'] == 'Yes':
      messages += [{"role": "system", "content": "The patient coughs up blood"}]
    else:
      messages += [{"role": "system", "content": "The patient does not cough up blood."}]

    fields = patientrows[0][92:94]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has{field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]

    if patient['Other Respiratory Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has{patient['Other Respiratory Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other respiratory symptoms are unknown. You must say that the patient does not have any other symptoms that affect The patient's breathing."}]

    # GENERAL SYMPTOMS: CARDIOVASCULAR
    # ['Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea']
    fields = patientrows[0][95:97]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has {field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not  have {field}"}]
    if patient['Syncope'] == 'Yes':
      messages += [{"role": "system", "content": "The patient faints"}]
    else:
      messages += [{"role": "system", "content": "The patient does not faint."}]
    if patient['Orthopnea'] == 'Yes':
      messages += [{"role": "system", "content": ""}]
    else:
      messages += [{"role": "system", "content": "The patient does not have shortness of breath while lying on their back."}]

    if patient['Other Cardiovascular Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has {patient['Other Cardiovascular Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other cardiovascular symptoms are unknown. You must say that the patient does not have any other symptoms that affect theart or blood."}]


    # GENERAL SYMPTOMS: GASTROINTESTINAL
    # ['Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice']
    fields = patientrows[0][100:107]
    for field in fields:
      if field == 'Dysphagia':
        if patient[field] == 'Yes':
          messages += [{"role": "system", "content": "The patient hasdifficulty swallowing."}]
        else:
          messages += [{"role": "system", "content": "The patient does not have difficulty swallowing."}]
      elif patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has{field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]

    if patient['Other Gastrointestinal Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has{patient['Other Gastrointestinal Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other gastrointestinal symptoms are unknown. You must say that the patient does not have any other symptoms that affect The patient's digestion."}]

    # GENERAL SYMPTOMS: GENITOURINARY
    # ['Nocturia', 'Dysuria', 'Frequency', 'Hematuria']
    if patient['Nocturia'] == 'Yes':
      messages += [{"role": "system", "content": "The patient pees a lot during the night"}]
    else:
      messages += [{"role": "system", "content": "The patient does not pee a lot during the night ."}]
    if patient['Dysuria'] == 'Yes':
      messages += [{"role": "system", "content": "The patient has pain when they pee."}]
    else:
      messages += [{"role": "system", "content": "The patient does not have pain when they pee."}]
    if patient['Urinary Frequency'] == 'Yes':
      messages += [{"role": "system", "content": "The patient pees more often than average"}]
    else:
      messages += [{"role": "system", "content": "The patient does not  pee more often than average ."}]
    if patient['Hematuria'] == 'Yes':
      messages += [{"role": "system", "content": "The patient has blood in their urine"}]
    else:
      messages += [{"role": "system", "content": "The patient does not have blood in their urine."}]

    if patient['Other Genitourinary Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has{patient['Other Genitourinary Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other genitourinary symptoms are unknown. You must say that you do not have any other symptoms that affect The patient's urine or The patient's reproductive system."}]

    # GENERAL SYMPTOMS: ENDOCRINE
    # ['Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance']
    fields = patientrows[0][113:118]
    for field in fields:
      if field == "Polyuria":
        if patient[field] == 'Yes':
          messages += [{"role": "system", "content": "The patient pees more than the average amount"}]
        else:
          messages += [{"role": "system", "content": "The patient does not pee more than the average amount ."}]
      elif patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"The patient has{field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]

    if patient['Other Endocrine Symptoms'] not in NA:
      messages += [{"role": "system", "content": f"The patient has{patient['Other Endocrine Symptoms']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other endocrine symptoms are unknown. You must say that you do not know any other symptoms that affect The patient's hormones."}]

    # PAST MEDICAL HISTORY
    # ["History of Tuberculosis", 'History of Asthma', 'History of Diabetes', 'History of Hypertension', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations', 'History of Allergies']
    fields = patientrows[0][119:127]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"{aggression if field in ['History of Diabetes', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations']else ''}The patient has{field}"}]
      else:
        messages += [{"role": "system", "content": f"{aggression if field in ['History of Diabetes', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations']else ''}The patient does not have {field}"}]

    if patient['Other Past Medical History'] not in NA:
      messages += [{"role": "system", "content": f"The patient has {patient['Other Past Medical History']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's other past medical history is unknown. You must say that you are not sure about The patient's past medical history."}]
    if patient['Cancer Site in History'] not in NA:
      messages += [{"role": "system", "content": f"the patient had cancer before at {patient['Cancer Site in History']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's previous cancer sites are unknown. You must say that you are not sure about previous cancer sites."}]
    if patient['Prior Surgeries Or Hospitalization Dates'] not in NA:
      messages += [{"role": "system", "content": f"the patient had prior surgeries or hospitalization dates on {patient['Prior Surgeries Or Hospitalization Dates']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's prior surgeries or hospitalization dates are unknown. You must say that you do not remember The patient's prior surgeries or hospitalization dates."}]
    if patient['Prior Surgeries Or Hospitalization Reasons'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}The patient has had prior surgeries or hospitalization because of {patient['Prior Surgeries Or Hospitalization Reasons']}"},]
    else:
      messages += [{"role": "system", "content": f"{aggression}The patient's prior surgeries or hospitalization reasons are unknown. You must say that you do not remember the reasons for The patient's prior surgeries or hospitalizations."}]
    if patient['Allergies in History'] not in NA:
      messages += [{"role": "system", "content": f"the patient had history of allergies with {patient['Allergies in History']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's history of allergies is unknown. You must say that you do not know about The patient's history of allergies."}]

    # FAMILY MEDICAL HISTORY
    # ['Family History of Tuberculosis', 'Family History of Asthma', 'Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer', 'Family History of Allergies']
    fields = patientrows[0][132:139]
    for field in fields:
      if patient[field] == 'Yes':
        messages += [{"role": "system", "content": f"{aggression if field in ['Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer'] else ''}The patient has {field}"}]
      else:
        messages += [{"role": "system", "content": f"{aggression if field in ['Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer'] else ''}The patient does not have {field}"}]

    if patient['Relationship To Cancer Patient'] not in NA:
      if patient['Cancer Site in Family History'] not in NA:
        messages += [{"role": "system", "content": f"The patient's {patient['Relationship To Cancer Patient']} has had cancer before at {patient['Cancer Site in Family History']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's {patient['Relationship To Cancer Patient']} has had cancer before."}]
    else:
      messages += [{"role": "system", "content": f"The patient's relationship to any cancer patient is unknown. You must say that you do not know if any of The patient's relatives have cancer or have had cancer."}]
    if patient['Allergies In Family History'] not in NA:
      messages += [{"role": "system", "content": f"The patient's family has had history of allergies with {patient['Allergies In Family History']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's family's history of allergies is unknown. You must say that you do not know about The patient's family's history of allergies."}]
    if patient['Other Family History'] not in NA:
      messages += [{"role": "system", "content": f"The patient's other family history is {patient['Other Family History']}"}]
    else:
      messages += [{"role": "system", "content": f"Other details about The patient's family history are unknown. You must say that you do not know about any other details about The patient's family history."}]
    if patient['Genogram (Describe Through Text)'] not in NA:
      messages += [{"role": "system", "content": f"The patient's genogram can be described as {patient['Genogram (Describe Through Text)']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's genogram is unknown. You must say that you do not know about The patient's family genogram."}]
    if patient['Social And Environmental History'] not in NA:
      messages += [{"role": "system", "content": f"The patient's social and environmental history can be described as {patient['Social And Environmental History']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's social and environmental history is unknown. You must say that you do not remember The patient's social and environmental history."}]

    # GYNECOLOGIC HISTORY
    if patient['Sex'] == 'Female' and patient['Menarche'] not in NA:
      if patient['Last Menstrual Period (YYYY-MM-DD)'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The start of The patient's last period or the first day of bleeding is {patient['Last Menstrual Period (YYYY-MM-DD)']}. You must answer in the format 'Month Day, Year'."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The start of The patient's last period or The patient's first day of bleeding is unknown. You must say that you do not remember the start of The patient's last period or The patient's first day of bleeding."}]
      if patient['Previous Menstrual Period (YYYY-MM-DD)'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The starting date of The patient's period before The patient's last is {patient['Previous Menstrual Period (YYYY-MM-DD)']}. You must answer in the format 'Month Day, Year'."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The starting date of The patient's period before The patient's last is unknown. You must say that you do not remember the starting date of The patient's period before The patient's last."}]
      if patient['Duration Of Menses'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The duration of period bleeding is {patient['Duration Of Menses']}."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The duration of The patient's period bleeding is unknown. You must say that you are not sure about how long The patient's period bleeding lasts."}]
      if patient['Interval Of Menses'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The interval of The patient's period cycles or how long each cycle takes is {patient['Interval Of Menses']}."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The interval of The patient's period cycles or how long each cycle takes is unknown. You must say that you are not sure about how long each cycle takes."}]
      if patient['Volume Of Menses'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}You bleed {patient['Volume Of Menses']} during The patient's period or menses."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The amount you bleed during The patient's period or menses is unknown. You must say that you are not sure about how much blood the patient expels during The patient's period."}]
      if patient['Menarche'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The patient was {patient['Menarche']} years old when she got her first period."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The patient's menarche or age when you got The patient's first period is unknown. You must say that you do not know when the patient had her first period."}]
      if patient['Coitarche'] not in NA:
        messages += [{"role": "system", "content": f"{aggression}The patient was {patient['Coitarche']} years old during first sexual intercourse."}]
      else:
        messages += [{"role": "system", "content": f"{aggression}The patient's coitarche or age during The patient's first sexual intercourse is unknown. You must say that you are unsure about the first time the patient had sex."}]

    # IMMUNIZATIONS
    # ['DPT/Polio Immunization', 'HIB Immunization', 'Hepatitis B Immunization', 'MMR Immunization', 'Measles Immunization', 'Varicella Immunization', 'Pneumococcal Immunization', 'Influenza Immunization', 'Hepatitis A Immunization']
    fields = patientrows[0][152:161]
    for field in fields:
      if patient[field] == 'Complete' or patient[field] == 'Incomplete':
        messages += [{"role": "system", "content": f"The patient has completed the doses for {patient[field]} {field}."}]
      elif patient[field] == 'None':
        messages += [{"role": "system", "content": f"The patient does not have {field}"}]
      else:
        messages += [{"role": "system", "content": f"The patient is unsure about whether the patient  has {field}. You must say that you do not know if the patient has{field}."}]

    # IMMUNIZATION DOSES
    # ['DPT/Polio Doses', 'HIB Doses', 'Hepatitis B Doses', 'MMR Doses', 'Measles Doses', 'Varicella Doses', 'Pneumococcal Doses', 'Influenza Doses', 'Hepatitis A Doses']
    fields = patientrows[0][161:170]
    for field in fields:
      if patient[field] not in NA:
        messages += [{"role": "system", "content": f"The patient has had {patient[field]} doses for {field}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's doses for {field} is unknown. You must say that you do not know how many {field} The patient has had."}]

    if patient['Patient First Name']+'-'+patient['Patient Last Name'] in immunization:
      messages += [{"role": "system", "content": f"The patient's immunizations include: {immunization[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's other immunizations are unknown. You must say that The patient is not sure about The patient's other immunizations."}]

    # ADOLESCENT INTERVIEW
    if patient['Home'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked about The patient's home, answer with {patient['Home']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about The patient's home is unknown. You must say that you do not want to talk about The patient's home."}]
    if patient['Education'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked about The patient's education, answer with {patient['Education']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about The patient's education is unknown. You must say that you do not want to talk about The patient's education."}]
    if patient['Activities'] not in NA:
      messages += [{"role": "system", "content": f"When asked about The patient's activities, answer with {patient['Activities']}."}]
    else:
      messages += [{"role": "system", "content": f"Information about The patient's activities is unknown. You must say that you do not want to talk about what you do."}]
    if patient['Drugs'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked about drugs The patient has taken, answer with {patient['Drugs']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about drugs The patient has taken is unknown. You must say that you do not want to talk about drugs."}]
    if patient['Sexual Activity'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked if The patient has had any kind of sexual activity or anything about it, answer with {patient['Sexual Activity']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about if the patient had any kind of sexual activity or anything about it is unknown. You must say that you do not want to talk about The patient's sex life."}]
    if patient['Suicide/Depression'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked about The patient's history with suicide or depression, answer with {patient['Suicide/Depression']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about The patient's history with suicide or depression is unknown. You must say that you do not want to talk about The patient's suicide or depression."}]
    if patient['Family'] not in NA:
      messages += [{"role": "system", "content": f"When asked about The patient's family, answer with {patient['Family']}."}]
    else:
      messages += [{"role": "system", "content": f"Information about The patient's family is unknown. You must say that you do not want to talk about The patient's family."}]
    if patient['Source Of Income And Dynamics'] not in NA:
      messages += [{"role": "system", "content": f"{aggression}When asked about The patient's source of income and dynamics, answer with {patient['Source Of Income And Dynamics']}."}]
    else:
      messages += [{"role": "system", "content": f"{aggression}Information about The patient's source of income and dynamics is unknown. You must say that you do not want to talk about The patient's source of income and dynamics."}]

    # NEUROPSYCHIATRIC EXAM
    # ['General Appearance', 'General Behavior', 'Attitude Towards Examiner', 'Mood', 'Affect', 'Speech', 'Perceptual Disturbance', 'Stream of Thought', 'Thought Content', 'Impulse Control', 'Intellectual Capacity Global Estimate']
    if patient['General Appearance'] not in NA:
      messages += [{"role": "system", "content": f"The patient's general appearance is {patient['General Appearance']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's general appearance is unremarkable."}]
    if patient['General Behavior'] not in NA:
      if patient['General Behavior'] == 'Normal':
        messages += [{"role": "system", "content": f"The patient's general behavior is normal."}]
      else:
        messages += [{"role": "system", "content": f"The patient is experiencing {patient['General Behavior']}"}]
    else:
      messages += [{"role": "system", "content": f"The patient's general behavior is unremarkable."}]
    if patient['Attitude Towards Examiner'] not in NA:
      messages += [{"role": "system", "content": f"The patient is {patient['Attitude Towards Examiner']} towards the examiner."}]
    else:
      messages += [{"role": "system", "content": f"The patient's attitude towards the examiner is unremarkable."}]
    if patient['Mood'] not in NA:
      messages += [{"role": "system", "content": f"The patient is feeling {patient['Mood']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's mood is unremarkable."}]
    if patient['Affect'] not in NA:
      affect = patient['Affect']
      if affect == 'Inappropriate':
        messages += [{"role": "system", "content": f"The patient's affect is inappropriate. The patient is demonstrating emotions that do not fit the context."}]
      if affect == 'Appropriate':
        messages += [{"role": "system", "content": f"The patient's affect is appropriate. The patient is demonstrating emotions that fit the context."}]
      if affect == 'Restricted':
        messages += [{"role": "system", "content": f"The patient's affect is restricted. The patient is demonstrating a narrow range of emotions."}]
      if affect == 'Blunted':
        messages += [{"role": "system", "content": f"The patient's affect is blunted. The patient is demonstrating a limited intensity of emotions."}]
      if affect == 'Flat':
        messages += [{"role": "system", "content": f"The patient's affect is flat. The patient is not demonstrating any emotions."}]
      if affect == 'Broad':
        messages += [{"role": "system", "content": f"The patient's affect is broad. The patient is able to demonstrate a broad range of emotions."}]
    else:
      messages += [{"role": "system", "content": f"The patient's affect is unremarkable."}]
    if patient['Speech'] not in NA:
      messages += [{"role": "system", "content": f"The patient's speech is {patient['Speech']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's speech is unremarkable."}]
    if patient['Perceptual Disturbance'] not in NA:
      perceptualDisturbance = patient['Perceptual Disturbance']
      if perceptualDisturbance == 'Derealization':
        messages += [{"role": "system", "content": f"The patient's perceptual disturbance is derealization. The patient feels detached from The patient's surroundings."}]
      if perceptualDisturbance == 'Depersonalization':
        messages += [{"role": "system", "content": f"The patient's perceptual disturbance is depersonalization. The patient feels detached and disconnected from The patient's self."}]
      if perceptualDisturbance == 'Hallucinations':
        messages += [{"role": "system", "content": f"The patient's perceptual disturbance is hallucinations. The patient is having hallucinations."}]
      if perceptualDisturbance == 'None':
        messages += [{"role": "system", "content": f"The patient's perceptual disturbance is none. The patient is not experiencing any perceptual disturbances."}]
    else:
      messages += [{"role": "system", "content": f"You don't remember any perceptual disturbances."}]
    if patient['Stream of Thought'] not in NA:
      stream = patient['Stream of Thought']
      if stream == 'Tangentiality':
        messages += [{"role": "system", "content": f"The patient's stream of thought is tangentiality. The patient's ideas are connected but they u tend to go far off-topic without returning to the initial topic."}]
      if stream == 'Paucity of Thought':
        messages += [{"role": "system", "content": f"The patient's stream of thought is paucity of thought. The patient is experiencing a paucity of thoughts."}]
      if stream == 'Flight of Ideas':
        messages += [{"role": "system", "content": f"The patient's stream of thought is flight of ideas. The patient talks quickly and erratically, jumping between ideas and thoughts."}]
      if stream == 'Looseness of Association':
        messages += [{"role": "system", "content": f"The patient's stream of thought is looseness of association. The patient's ideas lack connection."}]
      if stream == 'Goal Oriented':
        messages += [{"role": "system", "content": f"The patient's stream of thought is goal oriented. The patient's thoughts progress linearly without veering from the subject at hand."}]
    else:
      messages += [{"role": "system", "content": f"The patient's stream of thought is unremarkable."}]
    if patient['Thought Content'] not in NA:
      thought = patient['Thought Content']
      if thought == 'Suicidal':
        messages += [{"role": "system", "content": f"The patient's thought content is suicidal. The patient is experiencing suicidal thoughts."}]
      if thought == 'Bizzare':
        messages += [{"role": "system", "content": f"The patient's thought content is bizarre. The patient's thoughts can be describes as bizarre."}]
      if thought == 'Homicidal/Aggression':
        messages += [{"role": "system", "content": f"The patient's thought content is homicidal/aggression. The patient has homicidal thoughts and are prone to aggression."}]
      if thought == 'Grandiosity':
        messages += [{"role": "system", "content": f"The patient's thought content is grandiosity. The patient feels superior to others."}]
      if thought == 'Paranoia':
        messages += [{"role": "system", "content": f"The patient's thought content is paranoia. The patient is overly suspicious and are prone to thinking that others are out to harm them."}]
      if thought == 'Normal':
        messages += [{"role": "system", "content": f"The patient's thought content is normal. The patient's thoughts are normal."}]
    else:
      messages += [{"role": "system", "content": f"The patient's thoughts are unremarkable."}]
    if patient['Impulse Control'] not in NA:
      messages += [{"role": "system", "content": f"The patient is {patient['Impulse Control']} The patient's impulses."}]
    else:
      messages += [{"role": "system", "content": f"The patient's impulse control is unremarkable."}]
    if patient['Intellectual Capacity Global Estimate'] not in NA:
      messages += [{"role": "system", "content": f"The patient's intellectual capacity is {patient['Intellectual Capacity Global Estimate']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not know how smart The patient is on average."}]

    # NEUROPSYCHIATRIC EXAM: SENSORIUM
    # ['Consciousness', 'Other State of Consciousness', 'Attention Span', 'Attention Span Notes', 'Orientation Time', 'Orientation Place', 'Orientation Person', 'Memory', 'Memory Notes', 'Calculation', 'Calculation Notes', 'Fund of Information', 'Fund of Information Notes', 'Insight', 'Insight Notes', 'Judgment', 'Planning', 'Planning Notes', 'Speech Others', 'Other High Cortical Functions', 'Glasgow Scale GCS', 'Glasgow Coma Scale E', 'Glasgow Coma Scale V', 'Glasgow Coma Scale M']
    if patient['Consciousness'] not in NA:
      if patient['Consciousness'] == 'Stupor':
        messages += [{"role": "system", "content": f"The patient's consciousness is stupor. The patient is in a state of stupor."}]
      if patient['Consciousness'] == 'Coma':
        messages += [{"role": "system", "content": f"The patient's consciousness is coma. The patient is in a coma."}]
      else:
        messages += [{"role": "system", "content": f"The patient is {patient['Consciousness']}."}]
      if patient['Other State of Consciousness'] not in NA:
        messages += [{"role": "system", "content": f"The patient's state of consciousness can be also described with {patient['Other State of Consciousness']}."}]
    else:
      if patient['Other State of Consciousness'] not in NA:
        messages += [{"role": "system", "content": f"The patient's state of consciousness can be described with {patient['Other State of Consciousness']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's state of consciousness is unremarkable."}]
    if patient['Attention Span'] not in NA:
      messages += [{"role": "system", "content": f"The patient's attention span is {patient['Attention Span']}."}]
      if patient['Attention Span Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's attention span is also {patient['Attention Span Notes']}."}]
    else:
      if patient['Attention Span Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's attention span is {patient['Attention Span Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's attention span is unremarkable."}]
    if patient['Orientation Time'] not in NA:
      if patient['Orientation Time'] == 'Yes':
        messages += [{"role": "system", "content": f"The patient is able to correctly acknowledge the current time."}]
      if patient['Orientation Time'] == 'No':
        messages += [{"role": "system", "content": f"The patient is unable to correctly acknowledge the current time."}]
    else:
      messages += [{"role": "system", "content": f"The patient's disorientation/orientation when it comes to time is unremarkable."}]
    if patient['Orientation Place'] not in NA:
      if patient['Orientation Place'] == 'Yes':
        messages += [{"role": "system", "content": f"The patient is able to correctly acknowledge the current place."}]
      if patient['Orientation Place'] == 'No':
        messages += [{"role": "system", "content": f"The patient is unable to correctly acknowledge the current place."}]
    else:
      messages += [{"role": "system", "content": f"The patient's disorientation/orientation when it comes to place is unremarkable."}]
    if patient['Orientation Person'] not in NA:
      if patient['Orientation Person'] == 'Yes':
        messages += [{"role": "system", "content": f"The patient is able to correctly acknowledge The patient's identity."}]
      if patient['Orientation Person'] == 'No':
        messages += [{"role": "system", "content": f"The patient is unable to correctly acknowledge The patient's identity."}]
    else:
      messages += [{"role": "system", "content": f"The patient's disorientation/orientation when it comes to The patient's identity is unremarkable."}]
    if patient['Memory'] not in NA:
      messages += [{"role": "system", "content": f"The patient's memory is {patient['Memory']}."}]
      if patient['Memory Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's memory is also {patient['Memory Notes']}."}]
    else:
      if patient['Memory Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's memory is {patient['Memory Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's memory is unremarkable."}]
    if patient['Calculation'] not in NA:
      messages += [{"role": "system", "content": f"The patient's capability to perform calculations is {patient['Calculation']}."}]
      if patient['Calculation Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's capability to perform calculations is also {patient['Calculation Notes']}."}]
    else:
      if patient['Calculation Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's capability to perform calculations is {patient['Calculation Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's capability to perform calculations is unremarkable."}]
    if patient['Fund of Information'] not in NA:
      if patient['Fund of Information'] == 'Intact':
        messages += [{"role": "system", "content": f"The patient's fund of information is intact. They possess a satisfactory amount of general knowledge."}]
      if patient['Fund of Information'] == 'Deficient':
        messages += [{"role": "system", "content": f"The patient's fund of information is deficient. The patient's general knowledge is deficient."}]
      if patient['Fund of Information Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's fund of information is also {patient['Fund of Information Notes']}."}]
    else:
      if patient['Fund of Information Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's fund of information is {patient['Fund of Information Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's fund of information is unremarkable."}]
    if patient['Insight'] not in NA:
      if patient['Insight'] == 'Intact':
        messages += [{"role": "system", "content": f"The patient's insight is intact. They possess a good level of insight."}]
      if patient['Insight'] == 'Deficient':
        messages += [{"role": "system", "content": f"The patient's capacity for insight is deficient."}]
      if patient['Insight Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's insight is also {patient['Insight Notes']}."}]
    else:
      if patient['Insight Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's insight is {patient['Insight Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's insight is unremarkable."}]
    if patient['Judgment'] not in NA:
      messages += [{"role": "system", "content": f"The patient's capacity for good judgment is {patient['Judgment']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's capacity for good judgment is unremarkable."}]
    if patient['Planning'] not in NA:
      if patient['Planning'] == 'Intact':
        messages += [{"role": "system", "content": f"The patient's planning is intact. The patient is capable of planning."}]
      if patient['Planning'] == 'Deficient':
        messages += [{"role": "system", "content": f"The patient's planning is deficient. The patient is incapable of planning."}]
      if patient['Planning Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's capacity to plan is also {patient['Planning Notes']}."}]
    else:
      if patient['Planning Notes'] not in NA:
        messages += [{"role": "system", "content": f"The patient's capacity to plan is {patient['Planning Notes']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's capacity to plan is unremarkable."}]
    if patient['Speech Quality'] not in NA:
      speech = patient['Speech Quality']
      if speech == 'Dysphasia':
        messages += [{"role": "system", "content": f"The patient's speech quality is dysphasia. The patient is unable to comprehend or formulate language."}]
      if speech == 'Dysprosody':
        messages += [{"role": "system", "content": f"The patient's speech quality is dysprosody. The patient finds it difficult to control the way they speak."}]
      if speech == 'Dysarthria':
        messages += [{"role": "system", "content": f"The patient's speech quality is dysarthria. The patient's speech is slurred or slowed."}]
      if speech == 'Dysphonia':
        messages += [{"role": "system", "content": f"The patient's speech quality is dysphonia. The patient has poor voice quality."}]
      else:
        messages += [{"role": "system", "content": f"The patient's speech quality is {speech}."}]
      if patient['Speech Disorder Others'] not in NA:
        messages += [{"role": "system", "content": f"The patient's speech quality is also affected by {patient['Speech Disorder Others']}."}]
    else:
      if patient['Speech Disorder Others'] not in NA:
        messages += [{"role": "system", "content": f"The patient's speech quality is affected by {patient['Speech Disorder Others']}."}]
      else:
        messages += [{"role": "system", "content": f"The patient's speech quality is unremarkable."}]
    if patient['Other High Cortical Functions'] not in NA:
      if patient['Other High Cortical Functions'] == 'Apraxia':
        messages += [{"role": "system", "content": f"The patient's high cortical functions include apraxia. The patient is unable to perform certain actions."}]
      if patient['Other High Cortical Functions'] == 'Agnosia':
        messages += [{"role": "system", "content": f"The patient's high cortical functions include agnosia. The patient is incapable of identifying objects using one or more of The patient's senses."}]
    else:
      messages += [{"role": "system", "content": f"The patient's high cortical functions are unremarkable."}]
    if patient['Glasgow Coma Scale GCS'] not in NA:
      messages += [{"role": "system", "content": f"The patient's total Glasgow Coma Score is {patient['Glasgow Coma Scale GCS']}."}]
    else:
      messages += [{"role": "system", "content": f"You do not know The patient's Glasgow Coma Scale Score."}]
    if patient['Glasgow Coma Scale E'] not in NA:
      gcse = patient['Glasgow Coma Scale E']
      if gcse == '4':
        messages += [{"role": "system", "content": f"The patient's Eye Response score for the Glasgow Coma Scale is 4. The patient can open their eyes and keep them open on The patient's own."}]
      if gcse == '3':
        messages += [{"role": "system", "content": f"The patient's Eye Response score for the Glasgow Coma Scale is 3. The patient only open their eyes when someone tells them to do so."}]
      if gcse == '2':
        messages += [{"role": "system", "content": f"The patient's Eye Response score for the Glasgow Coma Scale is 2. The patient's eyes only open in response to feeling pressure."}]
      if gcse == '1':
        messages += [{"role": "system", "content": f"The patient's Eye Response score for the Glasgow Coma Scale is 1. The patient's eyes don't open for any reason."}]
    else:
      messages += [{"role": "system", "content": f"The patient does not know their Eye Response score for the Glasgow Coma Scale."}]
    if patient['Glasgow Coma Scale V'] not in NA:
      gcsv = patient['Glasgow Coma Scale V']
      if gcsv == '5':
        messages += [{"role": "system", "content": f"The patient's Verbal Response score for the Glasgow Coma Scale is 5. The patient can correctly answer questions about who they are, where they are, the day or year, and similar questions."}]
      if gcsv == '4':
        messages += [{"role": "system", "content": f"The patient's Verbal Response score for the Glasgow Coma Scale is 4. They can answer questions, but their answers show that they are not fully aware of what's happening."}]
      if gcsv == '3':
        messages += [{"role": "system", "content": f"The patient's Verbal Response score for the Glasgow Coma Scale is 3. They can talk and others can understand words you say, but their responses to questions don't make sense."}]
      if gcsv == '2':
        messages += [{"role": "system", "content": f"The patient's Verbal Response score for the Glasgow Coma Scale is 2. They can't talk and can only make sounds or noises."}]
      if gcsv == '1':
        messages += [{"role": "system", "content": f"The patient's Verbal Response score for the Glasgow Coma Scale is 1. They can't speak or make sounds."}]
    else:
      messages += [{"role": "system", "content": f"You do not know The patient's Verbal Response score for the Glasgow Coma Scale."}]
    if patient['Glasgow Coma Scale M'] not in NA:
      gcsm = patient['Glasgow Coma Scale M']
      if gcsm == '6':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 6. They follow instructions on how and when to move."}]
      if gcsm == '5':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 5. They intentionally move away from something that presses on them."}]
      if gcsm == '4':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 4. They only move away from something pressing on them as a reflex."}]
      if gcsm == '3':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 3. They flex muscles (pull inward) in response to pressure."}]
      if gcsm == '2':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 2. They extend muscles (stretch outward) in response to pressure."}]
      if gcsm == '1':
        messages += [{"role": "system", "content": f"The patient's Motor Response score for the Glasgow Coma Scale is 1. They don't move in response to pressure."}]
    else:
      messages += [{"role": "system", "content": f"You do not know The patient's Motor Response score for the Glasgow Coma Scale."}]

    # MEDICATIONS
    if patient['Patient First Name']+'-'+patient['Patient Last Name'] in medication:
      messages += [{"role": "system", "content": f"The patient's medication include: {medication[patient['Patient First Name']+'-'+patient['Patient Last Name']]}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's medication is unknown. You must say that The patient is not sure about the medication they have taken."}]

    # ADDITIONAL DETAILS
    if patient['Additional Details Regarding History'] not in NA:
      messages += [{"role": "system", "content": f"The patient's additional details regarding history include {patient['Additional Details Regarding History']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's additional details regarding history are unknown. You must say that you do not remember any additional details regarding The patient's history."}]
    if patient['Additional Details Regarding Context Including Ethical Considerations'] not in NA:
      messages += [{"role": "system", "content": f"The patient's additional details to help contextualize The patient's case, like ethical considerations include {patient['Additional Details Regarding Context Including Ethical Considerations']}."}]
    else:
      messages += [{"role": "system", "content": f"The patient's additional details regarding The patient's context are unknown. You must say that you do not remember any additional details regarding the patient's context."}]

    # for message in messages:
    #   print(message['content'])

    return messages

def get_mentor(n):
  mentorfieldscsv = [    
    ['Chief Complaint'], 
    ['Provocation', 'Quality', 'Region', 'Severity', 'Timing', 'Term', 'Delivered Via', 'To A (Age)', 'G', 'P', 'BW', 'Attended By First Name', 'Attended By Last Name', 'Perinatal CX', 'Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue', 'Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout', 'Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes', 'Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing', 'Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea', 'Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice', 'Nocturia', 'Dysuria', 'Urinary Frequency', 'Hematuria', 'Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance', 'History of Tuberculosis', 'History of Asthma', 'History of Diabetes', 'History of Hypertension', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations', 'History of Allergies', 'Cancer Site in History', 'Prior Surgeries Or Hospitalization Dates', 'Prior Surgeries Or Hospitalization Reasons', 'Allergies in History', 'Family History of Tuberculosis', 'Family History of Asthma', 'Family History of Psychiatric Consult', 'Family History of Diabetes', 'Family History of Cardiovascular Disease', 'Family History of Cancer', 'Family History of Allergies', 'Cancer Site in Family History', 'Relationship To Cancer Patient', 'Allergies In Family History', 'Genogram (Describe Through Text)', 'Social And Environmental History', 'Last Menstrual Period (YYYY-MM-DD)', 'Previous Menstrual Period (YYYY-MM-DD)', 'Duration Of Menses', 'Interval Of Menses', 'Volume Of Menses', 'Menarche', 'Coitarche', 'DPT/Polio Immunization', 'HIB Immunization', 'Hepatitis B Immunization', 'MMR Immunization', 'Measles Immunization', 'Varicella Immunization', 'Pneumococcal Immunization', 'Influenza Immunization', 'Hepatitis A Immunization', 'DPT/Polio Doses', 'HIB Doses', 'Hepatitis B Doses', 'MMR Doses', 'Measles Doses', 'Varicella Doses', 'Pneumococcal Doses', 'Influenza Doses', 'Hepatitis A Doses', 'Medications'], 
    ['Age', 'Sex', 'Provocation', 'Quality', 'Region', 'Severity', 'Timing', 'History Of Present Illness', 'Breastfed Till', 'Formula', 'Weaning Age', 'Current Diet', 'Food Allergy', 'Gross Motor', 'Adaptive-Fine Motor', 'Speech', 'Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue', 'Other General Symptoms', 'Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout', 'Other Musculoskeletal or Dermatologic Symptoms', 'Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes', 'Other HEENT Symptoms', 'Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing', 'Other Respiratory Symptoms', 'Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea', 'Other Cardiovascular Symptoms', 'Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice', 'Other Gastrointestinal Symptoms', 'Nocturia', 'Dysuria', 'Urinary Frequency', 'Hematuria', 'Other Genitourinary Symptoms', 'Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance', 'Other Endocrine Symptoms', 'History of Tuberculosis', 'History of Asthma', 'History of Diabetes', 'History of Hypertension', 'History of Psychiatric Consult', 'History of Cancer', 'Prior Surgeries/Hospitalizations', 'History of Allergies', 'Cancer Site in History', 'Prior Surgeries Or Hospitalization Dates', 'Prior Surgeries Or Hospitalization Reasons', 'Allergies in History', 'Other Past Medical History', 'Genogram (Describe Through Text)', 'Social And Environmental History', 'Last Menstrual Period (YYYY-MM-DD)', 'Previous Menstrual Period (YYYY-MM-DD)', 'Duration Of Menses', 'Interval Of Menses', 'Volume Of Menses', 'Menarche', 'Coitarche', 'DPT/Polio Immunization', 'HIB Immunization', 'Hepatitis B Immunization', 'MMR Immunization', 'Measles Immunization', 'Varicella Immunization', 'Pneumococcal Immunization', 'Influenza Immunization', 'Hepatitis A Immunization', 'DPT/Polio Doses', 'HIB Doses', 'Hepatitis B Doses', 'MMR Doses', 'Measles Doses', 'Varicella Doses', 'Pneumococcal Doses', 'Influenza Doses', 'Hepatitis A Doses', 'Other Immunizations', 'Activities', 'Drugs', 'Sexual Activity', 'Medications'], 
    ['Dwelling Type (House, Apt.)', 'Number Of Household Members', 'Religion', 'Annual Family Income', 'Stakeholder', "Stakeholder's Interest In Issue", "Stakeholder's Role", "Stakeholder's Level Of Influence", 'Pertinent Beliefs', 'Impact On Family', 'Facilitating', 'Hindering', 'Burden Of Illness', 'Pertinent Legislation Or Policies', 'Personal And Social', 'Home', 'Education', 'Activities', 'Drugs', 'Sexual Activity', 'Family', 'Source Of Income And Dynamics', 'Additional Details Regarding History', 'Additional Details Regarding Context Including Ethical Considerations', 'History of Psychiatric Consult'], 
    ['Nationality', 'Language', 'Religion', 'Pertinent Beliefs', 'Impact On Family', 'Facilitating', 'Hindering', 'Home', 'Education', 'Family', 'Additional Details Regarding Context Including Ethical Considerations'], 
    ['Provocation', 'Timing', 'Concerns Regarding Problem', 'Impact On Family', 'Facilitating', 'Hindering', 'Burden Of Illness', 'Pertinent Legislation Or Policies', 'Fever', 'Weight Gain', 'Weight Loss', 'Weakness', 'Fatigue', 'Other General Symptoms', 'Rashes', 'Lumps', 'Sores', 'Itching', 'Muscle Pains', 'Joint Pains', 'Changes in Skin Color', 'Joint Swelling', 'Changes in Hair/Nails', 'Gout', 'Headache', 'Dizziness', 'Blurring of Vision', 'Tinnitus', 'Deafness', 'Nosebleeds', 'Frequent Colds', 'Hoarseness', 'Dry Mouth', 'Gum Bleeding', 'Enlarged Lymph Nodes', 'Dyspnea', 'Hemoptysis', 'Cough', 'Wheezing', 'Palpitations', 'Chest Pains', 'Syncope', 'Orthopnea', 'Nausea', 'Vomiting', 'Dysphagia', 'Heartburn', 'Change in Bowel Habits', 'Rectal Bleeding', 'Jaundice', 'Nocturia', 'Dysuria', 'Urinary Frequency', 'Hematuria', 'Excessive Sweating', 'Heat Intolerance', 'Polyuria', 'Excessive Thirst', 'Cold Intolerance', 'Duration Of Menses', 'Volume Of Menses', 'Home', 'Activities', 'Drugs', 'Sexual Activity', 'Family'], 
    ['Chief Complaint', 'Concerns Regarding Problem', 'Additional Details Regarding History'], 
    ['Other General Symptoms', 'Other Musculoskeletal or Dermatologic Symptoms', 'Other HEENT Symptoms', 'Other Respiratory Symptoms', 'Other Cardiovascular Symptoms', 'Other Gastrointestinal Symptoms', 'Other Genitourinary Symptoms', 'Other Endocrine Symptoms', 'Other Past Medical History', 'Other Family History', 'Concerns Regarding Problem', 'Additional Details Regarding History', 'Additional Details Regarding Context Including Ethical Considerations'], 
    ['Chief Complaint', 'Specific', 'Physical/Physiological', 'Psychosocial/Emotional', 'Cultural Issues', 'Quality of Life Effect', 'Feelings', 'Additional']
]

  patient = {}
  for i in range(len(patientrows[0])):
    patient[patientrows[0][i]] = patientrows[int(n)][i]

  mentor_fields = {
    "Introduction": {"Introduction":0},
    "Agenda": {"Agenda":0},
    "Consent": {"Consent":0},
    "Confidentiality": {"Confidentiality":0},
    "Avoid Multiple": {"Avoid Multiple":1},
    "Order": {"Order": 1},
    "Recap": {"Recap":0},
    "Support": {"Support":0},
    "Closing": {"Closing":0},
  }
  NA = ["", "Not Applicable", "N/A", "NA", "not applicable"]
  for i in range(8):
    mentor_fields[mentorfieldscsv[8][i]] = {}
    for field in mentorfieldscsv[i]:
      if patient[field] not in NA:
        mentor_fields[mentorfieldscsv[8][i]][field] = 0

  return mentor_fields

def get_assistant_response(messages, model):
  if model == "Neutral":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:patient-eng-v11:Bb0jj7Oz",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  elif model == "Tagalog":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:patient-tag-v9:AsPwGQQi",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  elif model == "Taglish":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:patient-both-v9:B4IR9UW4",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  elif model == "Talkative":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:patient-talkative-v2:BEX03y9m",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  elif model == "Aggressive":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:patient-aggressive-v2:BEVtZ1bM",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  elif model == "Parent":
    r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:parent:BbOcbksn",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
  response = r.choices[0].message.content
  return response

def get_mentor_response(messages):
  r = client.chat.completions.create(
      model = "ft:gpt-4o-mini-2024-07-18:ateneo-school-of-medicine-and-public-health:mentor-v6:AjArl35r",
      messages=[{"role": m["role"], "content": m["content"]} for m in messages],
  )
  response = r.choices[0].message.content
  return response


## GUI ##


#Global Variables
userid = ""
patientid = ""
modelid = ""
patient_messages = {}
mentor_fields = {}
transcript = []
prev_order = -1
current_order = -1
patient_image = None
is_instructor = True
patientcode = ""
instructorid = ""

#Personality List -- Add to this dictionary if there is a new model
personality_list = {
            "Neutral" : "Neutral",
            "Talkative": "Talkative",
            "Aggressive" : "Aggressive"
        }

#Patient List 
patientcount = 0
for row in patientrows[1:]:
  if len(row) > 0 and row[0].strip():
    patientcount += 1

#Language List
language_list = {
    "English" : "English",
    "Tagalog" : "Tagalog",
    "Taglish" : "Taglish",
}
    
patient_list = {}

for patient in range(patientcount):
  patient_list[f"Patient {patient+1}"] = str(patient+1)


thinking_texts = [".", "..", "..."]
thinking_index = 0
thinking_animation_running = False
thinking_line_tag = "thinking_tag"
thinking_after_id = None

customtkinter.set_appearance_mode("system")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green


##Font Setup
import platform

#Temporarily store font data into memory during a session
if platform.system() == "Windows":
    from ctypes import windll
    font_path = resource_path("fonts/GlacialIndifference-Regular.ttf")
    FR_PRIVATE = 0x10
    windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

def get_font(size):
  try:
    return(customtkinter.CTkFont(family="Glacial Indifference", size=size))
  except:
    return (customtkinter.CTkFont(family="Arial", size=size))
  
appdir = os.path.dirname(os.path.abspath(__file__))
transcriptspath = os.path.join(appdir, "transcripts")
  

class App(customtkinter.CTk):
  def __init__(self):
    super().__init__()

    self.title("Caladrius")
    width = 600
    height = 600
    x = (self.winfo_screenwidth() // 2) - (width // 2)
    y = (self.winfo_screenheight() // 2) - (height // 2)
    self.geometry(f'{width}x{height}+{x}+{y}')
    self.resizable(False, False)

    self.frames = {}

    self.container = customtkinter.CTkFrame(self)
    self.container.pack(fill="both", expand=True)

    icon_path = resource_path("assets/Logo.ico")
    self.iconbitmap(icon_path)

    self.show_frame("UserIDPage")

  def show_frame(self, name):
      if name not in self.frames or name == "PatientStudentScreen" or name == "PatientInstructorScreen" or name == "ConversationScreen" or name == "ResultsScreen":
        frame_class = globals()[name]
        frame = frame_class(self.container, self)
        self.frames[name] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

      if name == "ConversationScreen":
        width = 1000
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
      elif name == "ResultsScreen":
        width = 1000
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
      else:
        width = 600
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

      self.frames[name].tkraise()


class UserIDPage(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    image_path = resource_path('assets/Logo.png')
    self.logo = customtkinter.CTkImage(light_image=Image.open(image_path),
                                  dark_image=Image.open(image_path),
                                  size=(400,200))
    
    self.logo_label = customtkinter.CTkLabel(self, text="", image=self.logo)
    self.logo_label.pack(pady=20)

    self.enteruidlabel = customtkinter.CTkLabel(self, text="Insert User ID:", font=get_font(24))
    self.enteruidlabel.place(relx=0.4, rely=0.5)

    self.entryuid = customtkinter.CTkEntry(self, height=50, width=200, text_color="#0C4D89", corner_radius=50, font=get_font(24), justify="center", fg_color=("white", "#B4B4B4"))
    self.entryuid.place(relx=0.35, rely=0.6)

    self.enteruidbutton = customtkinter.CTkButton(self, text="Enter", font=get_font(24), command=lambda:self.enteruid(None), fg_color="transparent", text_color = "#0C4D89", hover=False) 
    self.enteruidbutton.place(relx=0.4, rely=0.75)

    self.entryuid.bind("<Return>", self.enteruid)

  #Method when the user id is entered
  def enteruid(self, event):
    global userid
    global transcript
    if self.entryuid.get() == "":
        self.enteruidlabel.configure(text="You did not enter any User ID. Enter a User ID.")
        self.enteruidlabel.place(relx=0.15, rely=0.5)
    else:
        userid = self.entryuid.get()
        transcript.append("User ID    : " + self.entryuid.get())
        self.controller.show_frame("StartScreen")

class StartScreen(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    image_path = resource_path('assets/Logo.png')
    self.logo = customtkinter.CTkImage(light_image=Image.open(image_path),
                                  dark_image=Image.open(image_path),
                                  size=(400,200))
    
    self.logo_label = customtkinter.CTkLabel(self, text="", image=self.logo)
    self.logo_label.pack(pady=20)

    self.startbutton = customtkinter.CTkButton(self, text="Start", font=get_font(36), command=self.start, fg_color="transparent", text_color = "#0C4D89", hover=False)
    self.startbutton.place(relx=0.4, rely=0.5)

    self.exitbutton = customtkinter.CTkButton(self, text="Exit", font=get_font(36), command=self.exit, fg_color="transparent", text_color = "#0C4D89", hover=False)
    self.exitbutton.place(relx=0.4, rely=0.65)

  
  #Method for starting the program, leads to patient and personality window
  def start(self):
     if is_instructor == True:
        self.controller.show_frame("PatientInstructorScreen")
     else:
        self.controller.show_frame("PatientStudentScreen")
      
  #Method for exiting the program if exit is clicked
  def exit(self):
      self.controller.destroy()

  #Method for exiting the program on clicking the X button
  def on_close(self):
      self.controller.destroy()


class PatientStudentScreen(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    self.controller.protocol("WM_DELETE_WINDOW", self.on_close)

    self.selectpatientlabel = customtkinter.CTkLabel(self, text="Enter the patient code \nprovided by your instructor.", font=get_font(30))
    self.selectpatientlabel.place(relx=0.25, rely = 0.3)

    self.entrypatientcode = customtkinter.CTkEntry(self, 
                                                height=50, 
                                                width=410, 
                                                text_color="#0C4D89", 
                                                corner_radius=50,  
                                                font=get_font(24), 
                                                justify="center",
                                                fg_color=("white", "#B4B4B4"))
    self.entrypatientcode.place(relx=0.1875, rely=0.45)

    self.enterpatientbutton = customtkinter.CTkButton(self, 
                                                      text="Start", 
                                                      font=get_font(30), 
                                                      command=self.start, 
                                                      fg_color="transparent", 
                                                      text_color = "#0C4D89",
                                                      hover = False)
    self.enterpatientbutton.place(relx=0.4, rely=0.575)

  def on_close(self):
      self.controller.destroy()

  def start(self):
    patientcodeinput = self.entrypatientcode.get()
    self.processpatientcode(patientcodeinput)

  def processpatientcode(self, code):
      
      global patientid
      global modelid
      global patient_list
      global personality_list
      global transcript
      global patient_messages
      global mentor_fields
      global patient_image
      global patient_no
      global patientcode
      global instructorid

      patienthexlenstr = ""
      modelhexlenstr = []

      try:
          for c in code:
              if c == "-":
                  break
              
              patienthexlenstr += c

          for i in range(len(code)):
              if code[len(code) - 1 - i] == "-":
                  break

              if modelhexlenstr == "":
                  modelhexlenstr = code[len(code)-1-i]
                  continue

              modelhexlenstr.insert(0, code[len(code)-1-i])

          modelhexlenstr = ''.join(modelhexlenstr)

          code = code[len(patienthexlenstr)+1 : len(code)-len(modelhexlenstr)-1]
          # print("Processed Code (w/o info chars): " + code)
          # print("Patient Hex Length: " +  patienthexlenstr)
          # print("Personality Hex Length: " + modelhexlenstr)

          patienthexlen = int(patienthexlenstr)
          modelhexlen = int(modelhexlenstr)
          trimmed_code = code[patienthexlen:]
          # print("Trimmed Processed Code: " + trimmed_code)
          encinstructorid = ""
          # print("Is Trimmed Code Odd: " + str(len(trimmed_code) % 2 == 1))
          # print("Middle Index (Odd): " + str((len(trimmed_code) // 2)))
          # print("Middle Index (Even): " + str(((len(trimmed_code) // 2) - 1)))
          for i in range(len(trimmed_code)):
              if (trimmed_code[i] != trimmed_code[len(trimmed_code)-1-i]) or (((len(trimmed_code) % 2) == 1) and (i == (len(trimmed_code) // 2))) or (((len(trimmed_code) % 2) == 0) and (i == ((len(trimmed_code) // 2) - 1))):
                  break
              # print("I " + str(i))
              # print("Char: " + trimmed_code[i])
              # print("Reverse Char: " + trimmed_code[len(trimmed_code) - 1 - i])

              encinstructorid += trimmed_code[i]
          
          instructoridlen = len(encinstructorid)
          # print("Instructor ID Length: " + str(instructoridlen))

          raw_code = self.decrypt(code, instructoridlen+patienthexlen+modelhexlen)
          # print("Decrypted Code: " + raw_code)

          patienthex = "" 
          modelhex = ""

          for i in range(len(raw_code)):
              reverse_i = len(raw_code)- 1 - i
              if i == reverse_i:
                  break
              if i < patienthexlen:
                  patienthex += raw_code[i]
              if i >= patienthexlen and i < patienthexlen+instructoridlen:
                  instructorid += raw_code[i]
              if i >= patienthexlen+instructoridlen and i < patienthexlen+instructoridlen+modelhexlen:
                  modelhex += raw_code[i]

          # print("Patient Hex: " + patienthex)
          # print("Personality Hex: " + modelhex)
          # print("Instructor ID: " + instructorid)

          patientno = str(int(patienthex, 16))
          modelno = str(int(modelhex, 16))

          try:
            patientid = patient_list[f"Patient " + patientno]

            if modelno == "1":
              modelid = "Neutral"
            elif modelno == "2":
              modelid = "Tagalog"
            elif modelno == "3":
              modelid = "Taglish"
            elif modelno == "4":
              modelid = "Talkative"
            elif modelno == "5":
              modelid = "Aggressive"
            elif modelno == "6":
              modelid = "Parent"

            youngagedladiesfilenames = random.choice(['YoungLadyBlack.png', 'YoungLadyBrown.png'])
            middleagedladiesfilenames = random.choice(['MidLadyBlack.png', 'MidLadyBrown.png'])
            oldagedladiesfilenames = random.choice(['OldLady.png'])

            youngagedmenfilenames = random.choice(['YoungManBlack.png', 'YoungManBrown.png'])
            middleagedmenfilenames = random.choice(['MidManBlack.png', 'MidManBrown.png'])
            oldagedmenfilenames = random.choice(['OldMan.png'])

            transcript.append("Patient ID : " + patientid + "\n")
            transcript.append("Model      : " + modelid + "\n")
            patient = {}
            for i in range(len(patientrows[0])):
                patient[patientrows[0][i]] = patientrows[int(patientid)][i]
            if patient['Informant Relationship to Patient'] != "self":
                if patient['Informant Sex'] == "Female":
                    image_path = resource_path(f'PFP_Caladrius/Mid_Female/{middleagedladiesfilenames}')
                    patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                            dark_image=Image.open(image_path),
                                                            size=(250,250))
                elif patient['Informant Sex'] == "Male":
                    image_path = resource_path(f'PFP_Caladrius/Mid_Male/{middleagedmenfilenames}')
                    patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                            dark_image=Image.open(image_path),
                                                            size=(250,250))
                modelid = "Parent"
                patient_messages = get_patientfrominformant(patientid, modelid)
            else:
                if patient['Sex'] == "Female":
                    if int(patient['Age']) > 59:
                        image_path = resource_path(f'PFP_Caladrius/Old_Female/{oldagedladiesfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
                    elif 39 <= int(patient['Age']) < 59:
                        image_path = resource_path(f'PFP_Caladrius/Mid_Female/{middleagedladiesfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
                    elif 0 < int(patient['Age']) < 39:
                        image_path = resource_path(f'PFP_Caladrius/Young_Female/{youngagedladiesfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
                elif patient['Sex'] == "Male":
                    if int(patient['Age']) > 59:
                        image_path = resource_path(f'PFP_Caladrius/Old_Male/{oldagedmenfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
                    elif 39 <= int(patient['Age']) < 59:
                        image_path = resource_path(f'PFP_Caladrius/Mid_Male/{middleagedmenfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
                    elif 0 < int(patient['Age']) < 39:
                        image_path = resource_path(f'PFP_Caladrius/Young_Male/{youngagedmenfilenames}')
                        patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                                dark_image=Image.open(image_path),
                                                                size=(250,250))
        
            patient_messages = get_patient(patientid, modelid)
            mentor_fields = get_mentor(patientid)
            patient_no = modelid
            self.controller.show_frame("ConversationScreen")
          except:
            self.errorlabel = customtkinter.CTkLabel(self, text="Error on Patient Retrieval.", font=get_font(30))
            self.errorlabel.place(relx=0.25, rely = 0.68)

      except:
         mb.showwarning("Warning", "Wrong patient code. Please enter the correct patient code.")


  def decrypt(self, ciphertext, shift):

      plaintext = ""

      for c in ciphertext:
          unicode = ord(c)

          if unicode >= 48 and unicode <= 57:
              plaintext += chr((unicode - shift) if (unicode - shift) >= 48 else 58 - (48 - ((unicode + shift))))
          elif unicode >= 65 and unicode <= 90:
              plaintext += chr((unicode - shift) if (unicode - shift) >= 65 else 91 - (65 - ((unicode + shift))))
          elif unicode >= 97 and unicode <= 122:
              plaintext += chr((unicode - shift) if (unicode - shift) >= 97 else 123 - (97 - ((unicode + shift))))

      return plaintext
  

class PatientInstructorScreen(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    global patientiterator
    global personalityiterator
    global languageiterator
    patientiterator = None
    personalityiterator = None
    languageiterator = 0
    self.controller.protocol("WM_DELETE_WINDOW", self.on_close)
    buttonleftimage_path = resource_path('assets/buttonleft.png')
    buttonrightimage_path = resource_path('assets/buttonright.png')

    
    self.selectpatientlabel = customtkinter.CTkLabel(self, text="Select Patient", font=get_font(30))
    self.selectpatientlabel.place(relx=0.35, rely = 0.18)

    ## Patient Choice ##
    #Left Button for Patient Choice
    self.leftbuttonimage = customtkinter.CTkImage(light_image=Image.open(buttonleftimage_path),
                                  dark_image=Image.open(buttonleftimage_path),
                                  size=(50,50))
    
    
    self.leftbutton = customtkinter.CTkButton(self, 
                                              image=self.leftbuttonimage, 
                                              command=self.leftpatient,
                                              text="",
                                              width=20,
                                              height=20,
                                              fg_color="transparent",
                                              hover=False)
    self.leftbutton.place(relx=0.225, rely=0.23)

    #Right Button for Patient Choice
    self.rightbuttonimage = customtkinter.CTkImage(light_image=Image.open(buttonrightimage_path),
                                  dark_image=Image.open(buttonrightimage_path),
                                  size=(50,50))


    self.rightbutton = customtkinter.CTkButton(self, 
                                                image=self.rightbuttonimage, 
                                                command=self.rightpatient,
                                                text="",
                                                width=20,
                                                height=20,
                                                fg_color="transparent",
                                                hover=False)
    self.rightbutton.place(relx=0.67, rely=0.23)

    self.entrypatient = customtkinter.CTkEntry(self, 
                                                height=50, 
                                                width=210, 
                                                text_color="#0C4D89", 
                                                corner_radius=50, 
                                                state="disabled", 
                                                font=get_font(24), 
                                                justify="center",
                                                fg_color=("white", "#B4B4B4"))
    self.entrypatient.place(relx=0.3275, rely=0.24)
    ####

    ## Personality Choice ##
    self.selectpersonalitylabel = customtkinter.CTkLabel(self, text="Select Personality", font=get_font(30))
    self.selectpersonalitylabel.place(relx=0.32, rely=0.37)

    #Left Button for Personality Choice
    self.leftbutton2 = customtkinter.CTkButton(self, 
                                              image=self.leftbuttonimage, 
                                              command=self.leftpersonality,
                                              text="",
                                              width=20,
                                              height=20,
                                              fg_color="transparent",
                                              hover=False)
    self.leftbutton2.place(relx=0.225, rely=0.43)

    #Right Button for Personality Choice
    self.rightbutton2 = customtkinter.CTkButton(self, 
                                                image=self.rightbuttonimage, 
                                                command=self.rightpersonality,
                                                text="",
                                                width=20,
                                                height=20,
                                                fg_color="transparent",
                                                hover=False)
    self.rightbutton2.place(relx=0.67, rely=0.43)

    self.entrypersonality = customtkinter.CTkEntry(self, 
                                                    height=50, 
                                                    width=210, 
                                                    text_color="#0C4D89", 
                                                    corner_radius=50, 
                                                    font=get_font(24), 
                                                    justify="center", 
                                                    state="disabled",
                                                    fg_color=("white", "#B4B4B4"))
    self.entrypersonality.place(relx=0.3275, rely=0.44)

    ####

    ## Langauge Choice ##
    self.selectlanguagelabel = customtkinter.CTkLabel(self, text="Select Language", font=get_font(30))
    self.selectlanguagelabel.place(relx=0.32, rely=0.57)
    self.selectlanguagelabel.place_forget()
    
    #Left Button for Language Choice
    self.leftbutton3 = customtkinter.CTkButton(self, 
                                              image=self.leftbuttonimage, 
                                              command=self.leftlanguage,
                                              text="",
                                              width=20,
                                              height=20,
                                              fg_color="transparent",
                                              hover=False)
    self.leftbutton3.place(relx=0.225, rely=0.63)
    self.leftbutton3.place_forget()


    #Right Button for Language Choice
    self.rightbutton3 = customtkinter.CTkButton(self, 
                                                image=self.rightbuttonimage, 
                                                command=self.rightlanguage,
                                                text="",
                                                width=20,
                                                height=20,
                                                fg_color="transparent",
                                                hover=False) 
    self.rightbutton3.place(relx=0.67, rely=0.63)
    self.rightbutton3.place_forget()


    self.entrylanguage = customtkinter.CTkEntry(self, 
                                                    height=50, 
                                                    width=210, 
                                                    text_color="#0C4D89", 
                                                    corner_radius=50, 
                                                    font=get_font(24), 
                                                    justify="center", 
                                                    state="normal",
                                                    fg_color=("white", "#B4B4B4"))
    self.entrylanguage.place(relx=0.3275, rely=0.64)
    self.entrylanguage.insert(0, "English")
    self.entrylanguage.configure(state="disabled")
    self.entrylanguage.place_forget()

    ##

    self.enterpatientbutton = customtkinter.CTkButton(self, 
                                                      text="Start", 
                                                      font=get_font(30), 
                                                      command=self.start, 
                                                      fg_color="transparent", 
                                                      text_color = "#0C4D89",
                                                      hover = False)
    self.enterpatientbutton.place(relx=0.385, rely=0.8)




  #Method to go through patients with left button
  def leftpatient(self):
      global patientiterator
      global patient_list
      patientkey_list= list(patient_list.keys())

      if patientiterator == None:
          patientiterator = len(patient_list)-1
          self.entrypatient.configure(state="normal")
          self.entrypatient.insert(0, patientkey_list[patientiterator])
          self.entrypatient.configure(state="disabled")
      else:
          if patientiterator == 0:
              patientiterator = len(patient_list)-1
              self.entrypatient.configure(state="normal")
              self.entrypatient.delete(0, "end")
              self.entrypatient.insert(0, patientkey_list[patientiterator])
              self.entrypatient.configure(state="disabled")
          else:
              patientiterator -= 1
              self.entrypatient.configure(state="normal")
              self.entrypatient.delete(0, "end")
              self.entrypatient.insert(0, patientkey_list[patientiterator])
              self.entrypatient.configure(state="disabled")

  #Method to go through patients with right button
  def rightpatient(self):
      global patientiterator
      global patient_list
      patientkey_list= list(patient_list.keys())

      if patientiterator == None:
          patientiterator = 0
          self.entrypatient.configure(state="normal")
          self.entrypatient.insert(0, patientkey_list[patientiterator])
          self.entrypatient.configure(state="disabled")
      else:
          if patientiterator == len(patient_list)-1:
              patientiterator = 0
              self.entrypatient.configure(state="normal")
              self.entrypatient.delete(0, "end")
              self.entrypatient.insert(0, patientkey_list[patientiterator])
              self.entrypatient.configure(state="disabled")
          else:
              patientiterator += 1
              self.entrypatient.configure(state="normal")
              self.entrypatient.delete(0, "end")
              self.entrypatient.insert(0, patientkey_list[patientiterator])
              self.entrypatient.configure(state="disabled")


  #Method to go through personalities with left button
  def leftpersonality(self):
      global personalityiterator
      global personality_list
      global languageiterator
      selected_personality = None
      personalitykey_list=list(personality_list.keys())

      if personalityiterator == None:
          personalityiterator = len(personality_list)-1
          self.entrypersonality.configure(state="normal")
          self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
          selected_personality = self.entrypersonality.get()
          if selected_personality == "Neutral":
              self.selectlanguagelabel.place(relx=0.32, rely=0.57)
              self.leftbutton3.place(relx=0.225, rely=0.63)
              self.rightbutton3.place(relx=0.67, rely=0.63)
              self.entrylanguage.place(relx=0.3275, rely=0.64)
              self.entrylanguage.configure(state="normal")
          else:
              self.selectlanguagelabel.place_forget()
              self.leftbutton3.place_forget()
              self.rightbutton3.place_forget()
              self.entrylanguage.place_forget()
          self.entrypersonality.configure(state="disabled")
      else:
          if personalityiterator == 0:
              personalityiterator = len(personality_list)-1
              self.entrypersonality.configure(state="normal")
              self.entrypersonality.delete(0, "end")
              self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
              selected_personality = self.entrypersonality.get()
              if selected_personality == "Neutral":
                self.selectlanguagelabel.place(relx=0.32, rely=0.57)
                self.leftbutton3.place(relx=0.225, rely=0.63)
                self.rightbutton3.place(relx=0.67, rely=0.63)
                self.entrylanguage.place(relx=0.3275, rely=0.64)
                self.entrylanguage.configure(state="normal")
              else:
                self.selectlanguagelabel.place_forget()
                self.leftbutton3.place_forget()
                self.rightbutton3.place_forget()
                self.entrylanguage.configure(state="normal")
                self.entrylanguage.delete(0, "end")
                self.entrylanguage.insert(0, "English")
                languageiterator = 0
                self.entrylanguage.configure(state="disabled")
                self.entrylanguage.place_forget()
              self.entrypersonality.configure(state="disabled")
          else:
              personalityiterator -= 1
              self.entrypersonality.configure(state="normal")
              self.entrypersonality.delete(0, "end")
              self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
              selected_personality = self.entrypersonality.get()
              if selected_personality == "Neutral":
                self.selectlanguagelabel.place(relx=0.32, rely=0.57)
                self.leftbutton3.place(relx=0.225, rely=0.63)
                self.rightbutton3.place(relx=0.67, rely=0.63)
                self.entrylanguage.place(relx=0.3275, rely=0.64)
                self.entrylanguage.place(relx=0.3275, rely=0.64)
                self.entrylanguage.configure(state="normal")
              else:
                self.selectlanguagelabel.place_forget()
                self.leftbutton3.place_forget()
                self.rightbutton3.place_forget()
                self.entrylanguage.configure(state="normal")
                self.entrylanguage.delete(0, "end")
                self.entrylanguage.insert(0, "English")
                languageiterator = 0
                self.entrylanguage.configure(state="disabled")
                self.entrylanguage.place_forget()    
              self.entrypersonality.configure(state="disabled")

  #Method to go through personalities with right button
  def rightpersonality(self):
      global personalityiterator
      global personality_list
      global languageiterator
      selected_personality = None
      personalitykey_list=list(personality_list.keys())

      if personalityiterator == None:
          personalityiterator = 0
          self.entrypersonality.configure(state="normal")
          self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
          selected_personality = self.entrypersonality.get()
          if selected_personality == "Neutral":
              self.selectlanguagelabel.place(relx=0.32, rely=0.57)
              self.leftbutton3.place(relx=0.225, rely=0.63)
              self.rightbutton3.place(relx=0.67, rely=0.63)
              self.entrylanguage.place(relx=0.3275, rely=0.64)
              self.entrylanguage.configure(state="normal")
          else:
              self.selectlanguagelabel.place_forget()
              self.leftbutton3.place_forget()
              self.rightbutton3.place_forget()
              self.entrylanguage.place_forget()
              
          self.entrypersonality.configure(state="disabled")
      else:
          if personalityiterator == len(personality_list)-1:
              personalityiterator = 0
              self.entrypersonality.configure(state="normal")
              self.entrypersonality.delete(0, "end")
              self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
              selected_personality = self.entrypersonality.get()
              if selected_personality == "Neutral":
                self.selectlanguagelabel.place(relx=0.32, rely=0.57)
                self.leftbutton3.place(relx=0.225, rely=0.63)
                self.rightbutton3.place(relx=0.67, rely=0.63)
                self.entrylanguage.place(relx=0.3275, rely=0.64)
                self.entrylanguage.configure(state="normal")
              else:
                self.selectlanguagelabel.place_forget()
                self.leftbutton3.place_forget()
                self.rightbutton3.place_forget()
                self.entrylanguage.configure(state="normal")
                self.entrylanguage.delete(0, "end")
                self.entrylanguage.insert(0, "English")
                languageiterator = 0
                self.entrylanguage.configure(state="disabled")
                self.entrylanguage.place_forget()
              
          else:
              personalityiterator += 1
              self.entrypersonality.configure(state="normal")
              self.entrypersonality.delete(0, "end")
              self.entrypersonality.insert(0, personalitykey_list[personalityiterator])
              selected_personality = self.entrypersonality.get()
              if selected_personality == "Neutral":
                self.selectlanguagelabel.place(relx=0.32, rely=0.57)
                self.leftbutton3.place(relx=0.225, rely=0.63)
                self.rightbutton3.place(relx=0.67, rely=0.63)
                self.entrylanguage.place(relx=0.3275, rely=0.64)
                self.entrylanguage.configure(state="normal")
              else:
                self.selectlanguagelabel.place_forget()
                self.leftbutton3.place_forget()
                self.rightbutton3.place_forget()
                self.entrylanguage.configure(state="normal")
                self.entrylanguage.delete(0, "end")
                self.entrylanguage.insert(0, "English")
                languageiterator = 0
                self.entrylanguage.configure(state="disabled")
                self.entrylanguage.place_forget()
                  
              self.entrypersonality.configure(state="disabled")

  #Method to go through languages
  def leftlanguage(self):
      global languageiterator
      global language_list
      languagekey_list=list(language_list.keys())

      if languageiterator == 0:
          languageiterator = len(language_list)-1
          self.entrylanguage.configure(state="normal")
          self.entrylanguage.delete(0, "end")
          self.entrylanguage.insert(0, languagekey_list[languageiterator])
          self.entrylanguage.configure(state="disabled")
      else:
          languageiterator -= 1
          self.entrylanguage.configure(state="normal")
          self.entrylanguage.delete(0, "end")
          self.entrylanguage.insert(0, languagekey_list[languageiterator])
          self.entrylanguage.configure(state="disabled")

  def rightlanguage(self):
      global languageiterator
      global language_list
      languagekey_list=list(language_list.keys())

      if languageiterator == len(language_list)-1:
          languageiterator = 0
          self.entrylanguage.configure(state="normal")
          self.entrylanguage.delete(0, "end")
          self.entrylanguage.insert(0, languagekey_list[languageiterator])
          self.entrylanguage.configure(state="disabled")
      else:
          languageiterator += 1
          self.entrylanguage.configure(state="normal")
          self.entrylanguage.delete(0, "end")
          self.entrylanguage.insert(0, languagekey_list[languageiterator])
          self.entrylanguage.configure(state="disabled")
          
  def generatepatientcode(self, userid, patientid, modelid):

    model_map ={
      "Neutral": 1,
      "Tagalog": 2,
      "Taglish": 3,
      "Talkative": 4,
      "Agressive": 5,
      "Parent": 6
    }

    try:
      modelno = model_map[modelid]
    except KeyError:
      raise ValueError(f"Unknown modelid: {modelid}")
    patient_hex = hex(int(patientid))[2:]
    model_hex = hex(modelno)[2:]
    

    raw_code = patient_hex + str(userid) + model_hex + str(userid)[::-1] 
    
    patient_hexlength = len(patient_hex)
    model_hexlength = len(model_hex)

    # print("Instructor ID Length: " + str(len(userid)))
    # print("Patient Hex Length: " + str(len(patient_hex)))
    # print("Personality Hex Length: " + str(len(model_hex)))
    # print("Raw Code (Before Encryption): " + raw_code)

    s = len(userid) + patient_hexlength + model_hexlength

    # print("S: " + str(s))
    encryptedcode = self.encrypt(raw_code, s)
    # print("Encrypted Code (w/o info chars): " + encryptedcode)

    return str(patient_hexlength) + "-" + encryptedcode + "-" + str(model_hexlength)

  def encrypt(self, plaintext, shift):

    cipher = ""

    for c in plaintext:
        unicode = ord(c)

        if unicode >= 48 and unicode <= 57:
            cipher += chr((unicode + shift) if (unicode + shift) <= 57 else (47 + ((unicode + shift) % 57)))
        elif unicode >= 65 and unicode <= 90:
            cipher += chr((unicode + shift) if (unicode + shift) <= 90 else (64 + ((unicode + shift) % 90)))
        elif unicode >= 97 and unicode <= 122:
            cipher += chr((unicode + shift) if (unicode + shift) <= 122 else (96 + ((unicode + shift) % 122)))

    return cipher
  
  #Method to start conversation with patient with a given patient and personality
  def start(self):
      global patientid
      global modelid
      global patient_list
      global personality_list
      global transcript
      global patient_messages
      global mentor_fields
      global patient_image
      global patient_no
      global patientcode
      global instructorid

      try:
        youngagedladiesfilenames = random.choice(['YoungLadyBlack.png', 'YoungLadyBrown.png'])
        middleagedladiesfilenames = random.choice(['MidLadyBlack.png', 'MidLadyBrown.png'])
        oldagedladiesfilenames = random.choice(['OldLady.png'])

        youngagedmenfilenames = random.choice(['YoungManBlack.png', 'YoungManBrown.png'])
        middleagedmenfilenames = random.choice(['MidManBlack.png', 'MidManBrown.png'])
        oldagedmenfilenames = random.choice(['OldMan.png'])

        if self.entrypatient.get() == "" or self.entrypersonality.get() == "":
            mb.showwarning("Warning", "No Patient or Personality Chosen! Please choose a patient and/or a personality.")
        else:
            patientinput = self.entrypatient.get()
            modelinput = self.entrypersonality.get()
            patientid = patient_list[patientinput]
            modelid = personality_list[modelinput]
            if modelid == "Neutral":
                languageinput = self.entrylanguage.get()
                if languageinput == "Tagalog":
                  modelid = "Tagalog" 
                elif languageinput == "Taglish":
                  modelid = "Taglish"
            transcript.append("Patient ID : " + patientid + "\n")
            transcript.append("Model      : " + modelid + "\n")
            patient = {}
            for i in range(len(patientrows[0])):
              patient[patientrows[0][i]] = patientrows[int(patientid)][i]
            if patient['Informant Relationship to Patient'] != "self":
              if patient['Informant Sex'] == "Female":
                image_path = resource_path(f'PFP_Caladrius/Mid_Female/{middleagedladiesfilenames}')
                patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
              elif patient['Informant Sex'] == "Male":
                image_path = resource_path(f'PFP_Caladrius/Mid_Male/{middleagedmenfilenames}')
                patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
              modelid = "Parent"
              patient_messages = get_patientfrominformant(patientid, modelid)
            else:
              if patient['Sex'] == "Female":
                if int(patient['Age']) > 59:
                  image_path = resource_path(f'PFP_Caladrius/Old_Female/{oldagedladiesfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
                elif 39 <= int(patient['Age']) < 59:
                  image_path = resource_path(f'PFP_Caladrius/Mid_Female/{middleagedladiesfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
                elif 0 < int(patient['Age']) < 39:
                  image_path = resource_path(f'PFP_Caladrius/Young_Female/{youngagedladiesfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
              elif patient['Sex'] == "Male":
                if int(patient['Age']) > 59:
                  image_path = resource_path(f'PFP_Caladrius/Old_Male/{oldagedmenfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
                elif 39 <= int(patient['Age']) < 59:
                  image_path = resource_path(f'PFP_Caladrius/Mid_Male/{middleagedmenfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
                elif 0 < int(patient['Age']) < 39:
                  image_path = resource_path(f'PFP_Caladrius/Young_Male/{youngagedmenfilenames}')
                  patient_image = customtkinter.CTkImage(light_image=Image.open(image_path),
                                                      dark_image=Image.open(image_path),
                                                      size=(250,250))
                  
              patient_messages = get_patient(patientid, modelid)

            mentor_fields = get_mentor(patientid)
            patientcode = self.generatepatientcode(userid, patientid, modelid)
            patient_no = modelid
            instructorid = userid
            self.controller.show_frame("ConversationScreen")
            
      except:
          self.errorlabel = customtkinter.CTkLabel(self, text="Error on Patient Retrieval.", font=get_font(30))
          self.errorlabel.place(relx=0.25, rely = 0.68)
  


  #Method for exiting the program on clicking the X button
  def on_close(self):
      self.controller.destroy()

class ConversationScreen(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
    global patient_image
    global patientcode
    global is_instructor
    buttonrightimage_path = resource_path('assets/buttonright.png')

    super().__init__(parent, fg_color="#0C4D89")
    self.controller = controller

    self.controller.protocol("WM_DELETE_WINDOW", self.on_close)

    self.convoframe = customtkinter.CTkFrame(self, 
                                              fg_color="white",
                                              width=675,
                                              height=580,
                                              corner_radius=20)
    self.convoframe.place(relx=0.02, rely=0.02)

    self.patientframe = customtkinter.CTkFrame(self, 
                                              fg_color="white",
                                              width=280,
                                              height=580,
                                              corner_radius=20)
    self.patientframe.place(relx=0.71, rely=0.02)

    self.convotext = customtkinter.CTkTextbox(self.convoframe, 
                                              fg_color="white",
                                              font=get_font(16),
                                              corner_radius=20,
                                              text_color="black",
                                              width=660,
                                              height=510,
                                              state="disabled")
    self.convotext.place(relx=0.01, rely=0.01)
    self.convotext.bind("<Key>", lambda command: "break") 
    self.convotext.bind("<Button-1>", lambda command: "break") 
    self.convotext.bind("<B1-Motion>", lambda command: "break") 
    self.convotext.bind("<Double-1>", lambda command: "break")
    self.convotext.bind("<Button-2>", lambda command: "break")  
    self.convotext.bind("<Button-3>", lambda command: "break") 

    self.convoentry = customtkinter.CTkEntry(self.convoframe,
                                              placeholder_text="Enter here",
                                              height=50,
                                              width=600,
                                              corner_radius=50,
                                              fg_color=("white", "white"),
                                              text_color=("black"),
                                              font=get_font(24),
                                              )
    self.convoentry.place(relx=0.01, rely=0.9)

    #Send Button Image
    self.rightbuttonimage = customtkinter.CTkImage(light_image=Image.open(buttonrightimage_path),
                                  dark_image=Image.open(buttonrightimage_path),
                                  size=(40,40))

    self.sendbutton = customtkinter.CTkButton(self.convoframe, 
                                                image=self.rightbuttonimage, 
                                                command=lambda:self._on_execute(None),
                                                text="",
                                                width=40,
                                                height=40,
                                                fg_color="transparent",
                                                hover=False)
    self.sendbutton.place(relx=0.9, rely=0.9)


    self.patient = customtkinter.CTkLabel(self.patientframe,
                                          image=patient_image,
                                          text="")
    self.patient.place(relx=0.06,rely=0.03)

    self.patientlabel = customtkinter.CTkLabel(self.patientframe,
                                                fg_color="transparent",
                                                font=get_font(36),
                                                text=f'Patient {patientid}',
                                                text_color="#0C4D89",
                                                width=50,
                                                height=50)
    self.patientlabel.place(relx=0.25, rely=0.475)

    self.endconvo = customtkinter.CTkButton(self.patientframe,
                                            fg_color="transparent",
                                            font=get_font(24),
                                            text="End Conversation",
                                            text_color="#0C4D89",
                                            width=20,
                                            height=20,
                                            corner_radius=50,
                                            command=self.end_convo,
                                            hover=False)
    self.endconvo.place(relx=0.15, rely=0.9)

    self.patientcodelabel = customtkinter.CTkLabel(self.patientframe,
                                                   fg_color="transparent",
                                                   font=get_font(24),
                                                   text=f'The patient code is:\n{patientcode}',
                                                   text_color="#0C4D89",
                                                   width=50,
                                                   height=50)
    if is_instructor == True:
      self.patientcodelabel.place(relx=0.12, rely=0.65)

    self.convoentry.bind("<Return>", self._on_execute)

  #Method to end the conversation
  def end_convo(self):
      response = mb.askquestion("End Conversation?", "Are you sure you want to end the conversation?")
      if response == 'yes':
          self.controller.show_frame("ResultsScreen")
          
  #Method for exiting the program on clicking the X button
  def on_close(self):
      self.controller.destroy()

  def animate_entry_loading(self):
    global thinking_index, thinking_after_id
    if thinking_animation_running:
        thinking_message = thinking_texts[thinking_index % len(thinking_texts)]
        ranges = self.convotext.tag_ranges(thinking_line_tag)
        if not ranges:
            self.convotext.insert(END, f"{thinking_message}", thinking_line_tag)
        else:
          if ranges:
            self.convotext.delete(ranges[0], ranges[1])
            self.convotext.insert(ranges[0], thinking_message, thinking_line_tag)
        self.convotext.see(END)
        thinking_index += 1
        thinking_after_id = self.after(1000, self.animate_entry_loading)

  #Method to send a message to the patient
  def _on_enter_pressed(self):
      user_input = self.convoentry.get()
      self.convotext.configure(state=NORMAL)
      self.convoentry.delete(0, END)
      self.convoentry.configure(state=DISABLED)
      self.sendbutton.configure(state=DISABLED) 

      global patient_messages
      global mentor_fields
      global transcript
      global userid
      global patientid
      global modelid
      global prev_order
      global current_order
      
      
      user_msg = f"Doctor: {user_input}\n"
      self.convotext.insert(END, user_msg)


      try:    
        patient_messages.append({"role": "user", "content": user_input})
        mentor_messages.append({"role": "user", "content": user_input})

        assistant_response = get_assistant_response(patient_messages, modelid)
        patient_messages.append({"role": "assistant", "content": assistant_response})
        patient_msg = f"Patient: {assistant_response}\n"
        self.convotext.delete("end-1l", "end")
        self.convotext.insert(END, f"\n{patient_msg}")
            
        mentor_response = get_mentor_response(mentor_messages)
        mentor_messages.append({"role": "assistant", "content": mentor_response})
        mentor_msg = f"Mentor: {mentor_response}\n\n"
        self.convotext.delete("end-1l", "end")
        self.convotext.insert(END, f"\n{mentor_msg}")
        
            
        transcript.append(f"{user_msg}{patient_msg}{mentor_msg}")

        mentor_response = [response.strip(" ").split(":") for response in mentor_response.split(";")]
        for response in mentor_response:
            for key, value in mentor_fields.items():
                if response[0] in value.keys():
                    value[response[0]] = response[1]

            # ORDER
            for item in order_fields:
                if response[0] in item:
                    current_order = order_fields.index(item)
            if current_order < prev_order:
                mentor_fields['Order']['Order'] = 0
                transcript.append("Mentor : Order:0")
            prev_order = current_order
      except:
          self.convotext.insert(END, "Error occurred on generating a response. Please try again.\n\n")
      
      self.stop_thinking()
      self.convotext.see(END)
      self.convotext.configure(state=DISABLED)
      self.convoentry.configure(state=NORMAL)
      self.sendbutton.configure(state=NORMAL)

  def stop_thinking(self):
      global thinking_animation_running, thinking_after_id
      thinking_animation_running = False
      if thinking_after_id:
        self.after_cancel(thinking_after_id)
        thinking_after_id = None
      ranges = self.convotext.tag_ranges(thinking_line_tag)
      if ranges:
          self.convotext.delete(ranges[0], ranges[1])
          self.convotext.tag_remove(thinking_line_tag, "1.0", END)
      self.convotext.see("end")

  def _on_execute(self, event=None):
      global thinking_animation_running, thinking_index, thinking_after_id
      thinking_animation_running = True
      thinking_index = 0
      self.after(100, self.animate_entry_loading())
      Thread(target=self._on_enter_pressed, daemon=True).start()


class ResultsScreen(customtkinter.CTkFrame):
  def __init__(self, parent, controller):
      global userid
      global prev_order
      global current_order
      global instructorid
      super().__init__(parent)

      self.controller = controller

      self.controller.protocol("WM_DELETE_WINDOW", self.on_close)

      self.transcriptmade = customtkinter.CTkLabel(self, 
                                                  text=f"\n\nYour conversation has been saved to transcript_{userid}_{datetime.datetime.now().strftime('%d%m%y_%H%M%S')}.txt",
                                                  font=get_font(24),
                                                  text_color = "#0C4D89")
      self.transcriptmade.place(relx=0.15)

      msg = ""
      msg += "Criteria\t\t\tScore\n"
      msg
      transcript.append("\nCriteria                Score")
      for key, value in mentor_fields.items():
          avg = 0
          for score in value.values():
              avg += float(score)
          if configcsv[key] != "0":
              msg += "{}\t\t\t{:>5}%\n".format(key.ljust(24), int(avg/len(value)*100))
              transcript.append("{}{:.0f}%".format(key.ljust(24), avg/len(value)*100))

      self.results = customtkinter.CTkTextbox(self,
                                            font=get_font(20),
                                            corner_radius=20,
                                            text_color="black",
                                            width=400,
                                            height=500,
                                            state="disabled",
                                            fg_color=("white", "#B4B4B4"))
      self.results.place(relx=0.3, rely=0.13)
      self.results.configure(state="normal")
      self.results.insert("0.0", msg)
      self.results.configure(state="disabled")
      msg += "-----------------------------\n\n"
      transcript.append("-----------------------------\n")
      if len(transcript) > 0:
        os.makedirs("transcripts", exist_ok=True)
        filename = "transcript_" + userid + "_" + datetime.datetime.now().strftime("%d%m%y_%H%M%S") + ".txt"
        filepath = os.path.join("transcripts", filename)
        with open(filepath, "w") as file:
          for i in transcript:
              file.write(str(i) + "\n")
        if platform.system() == "Windows":
          os.chmod(filepath, stat.S_IREAD)
        else:
          os.chmod(filepath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        if instructorid == "001":
          folder_id = "19IOzaFVMrWrOczdZEs0GynfGUvBIq6jp"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
        elif instructorid == "002":
          folder_id = "1yJ4UTEFF_ICn0CuKeq69C-wgA1yu-4c9"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
        elif instructorid == "003":
          folder_id = "10d_YVNeZWTQJ0UMN8uOfqS07vcUyBJAM"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
        elif instructorid == "004":
          folder_id = "1mTzsvxeoPwFyG7JWGXYHcdmp1LcgwVoH"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
        elif instructorid == "005":
          folder_id = "1yRV4OPH83LQ3-Qlf7U6AB0Rclyybz-Dg"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
        else:
          folder_id = "1phdXo4G7RF4C6UEkzzwTfB8Zc0B9ghpW"
          file_metadata = {
            "name": filename,
            "parents": [folder_id]  # Put in specific folder
          }
          media = MediaFileUpload(filepath, mimetype="text/plain")
          uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
          ).execute()
         

      self.resimulatequestion = customtkinter.CTkLabel(self, 
                                                    text="Do you want to resimulate?",
                                                    font=get_font(24),
                                                    text_color = "#0C4D89")
      self.resimulatequestion.place(relx=0.37, rely=0.85)

      self.yesresimulatebutton = customtkinter.CTkButton(self,
                                                    text="Yes",
                                                    font=get_font(24), 
                                                    command=self.yesresimulate, 
                                                    fg_color="transparent", 
                                                    text_color = "#0C4D89",
                                                    hover=False)
    
      self.yesresimulatebutton.place(relx=0.4, rely=0.9)

      self.noresimulatebutton = customtkinter.CTkButton(self,
                                                    text="No",
                                                    font=get_font(24), 
                                                    command=self.noresimulate, 
                                                    fg_color="transparent", 
                                                    text_color = "#0C4D89",
                                                    hover=False)
    
      self.noresimulatebutton.place(relx=0.5, rely=0.9)

      msg = []        
      prev_order = -1
      current_order = -1

  #Method for exiting the program on clicking the X button
  def on_close(self):
      self.controller.destroy()
      
  #Method to resimulate
  def yesresimulate(self):
      global transcript
      transcript = []
      transcript.append("User ID    : " + userid)
      self.controller.show_frame("StartScreen")

  #Method to not resimulate and close the program
  def noresimulate(self):
      self.controller.destroy()


#Start the program
caladrius = App()
caladrius.mainloop()


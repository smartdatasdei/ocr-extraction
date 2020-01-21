#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:10:42 2019

@author: chiranshub
"""
# from azure.cognitiveservices.vision.computervision import ComputerVisionClient
# from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
# from azure.cognitiveservices.vision.computervision.models import TextRecognitionMode
# from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
# from msrest.authentication import CognitiveServicesCredentials
import json
import os
import sys
import time
import requests
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials
import re
# from pdf_to_png import pdf_to_png

# variables for entity extraction from text
key_var_name = '6bdd881462d54d91ae529805aa41b2f7'#'2f77f291c6e8467c8c694bd80a445f9a'
endpoint_var_name = 'https://hcdf-text.cognitiveservices.azure.com/'#'https://hcdf-form-text.cognitiveservices.azure.com/'
credentials = CognitiveServicesCredentials(key_var_name)
text_analytics = TextAnalyticsClient(endpoint=endpoint_var_name, credentials=credentials)
def find_pattern(text, patterns):
    if re.search(patterns, text):
        return re.search(patterns, text)
    else:
        return False
def extract_entities(t):
    documents = [
        {
            "id": "1",
            "language": "en",
            "text": t
        }
    ]
    response = text_analytics.entities(documents=documents)
    return response


class ocr_extraction:
    def __init__(self):
        self.subscription_key='3e19496d743742c8852df11550dd0428'#'d7d1fec58933440fa89fcfd8f9b58a06'
        self.endpoint='https://hcdf-ocr.cognitiveservices.azure.com/'#'https://hcdf-form.cognitiveservices.azure.com/'
        self.ocr_url = self.endpoint + "vision/v2.1/ocr"
        self.params = {'language': 'en', 'detectOrientation': 'true'}
        self.text=[]
        
    def text_extract(self,image_data):
        headers = {'Ocp-Apim-Subscription-Key': self.subscription_key, 'Content-Type': 'application/octet-stream'}
        response = requests.post(self.ocr_url, headers=headers, params=self.params, data = image_data)
        if response.status_code==200:
            print("conversion successful")
            ext=json.loads(response.text)
            for x in ext['regions']:
                line=[]
                line=[q['text'] for w in x['lines'] for q in w['words']]
                print(line)
                self.text.append(" ".join(line))
            text_new=" ".join(self.text)
    
            text_new=re.split('[0-9]{1,2}\.| [a-z]{1}\.',text_new)
            return text_new
        else:
            print(response.status_code)
            print("raise_exception")
            
            
class entity_extraction:
    def __init__(self):
        self.info={}
        # define regex for every feild
        self.reg_pt_name='PATIENT\'S NAME'
        self.reg_ins_name='INSURED\'S NAME'
        self.reg_ins_add='INSURED\'S ADDRESS|CITY|TELEPHONE'
        self.reg_ins_policy='INSURED\'S POLICY GROUP'
        self.reg_amt='AMOUNT PAID'
        self.reg_charge='TOTAL CHARGE .{2,3}[0-9]*'
        self.reg_qual='QUAL'
        self.reg_render='RENDERING.*PROVIDER'
        self.reg_ins_num='INSURED.*NUMBER'
        self.reg_comp_name='BLU.*CROSS.*BLUE'
        self.reg_comp_add='CPT/HCP'
        self.reg_federal='FEDERAL TAX'
        
    def pt_name(self,text):
    # regex to extract for patient name 
        rem='\(.*\)'
#        reg_name='PATIENT\'S NAME' # haven't used yet , check later for use
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
        text=text.replace(',','')
    #     print(text)
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if entity.type in 'Person':
                    self.info['Patients Name']=entity.name
        return self.info
    # func to extract insured name 

    def ins_name(self,text):
        # regex to extract for patient name 
        rem='\(.*\)'
    #    reg_name='INSURED\'S NAME' # haven't used yet , check later for use
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
        text=text.replace(',','')
    #     print(text)
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if entity.type in 'Person':
                    self.info['Insured\'s Name']=entity.name
        return self.info
    

    def ins_add(self,text):
        # regex to extract for patient name 
        rem='\(.*?\)'
#        reg_name='INSURED\'S ADDRESS' # haven't used yet , check later for use
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
        text=text.replace(',','')
        print(text)
        # first we check that if text contains city then extract text
        # before that
        reg_city='CITY'
    #     text=text.lower()
        to_remove=find_pattern(text,reg_city)
        if to_remove!=False:
            text_ins_add=text[:to_remove.span()[0]] 
            print("text_ins_add",text_ins_add)
            resp=extract_entities(text_ins_add)
            for document in resp.documents:
                for entity in document.entities:
                    if entity.type in 'Location':
                        self.info['Insured\'s Address']=entity.name
        # check if string contains city than extract city
            text_ins_city=text[to_remove.span()[0]:]
            print(text_ins_city)
            resp=extract_entities(text_ins_city)
            for document in resp.documents:
                for entity in document.entities:
                    if entity.type in 'Location':
                        self.info['City']=entity.name
        # check if it contains telephone 
        reg_telephone='TELEPHONE'
        to_remove=find_pattern(text,reg_telephone)
        if to_remove!=False:
            text_ins_telephone=text[to_remove.span()[0]:] 
            to_remove=find_pattern(text_ins_telephone,rem)
    #         text_ins_telephone=text_ins_telephone[0:to_remove.span()[0]]+text_ins_telephone[to_remove[1]+1:]
            resp=extract_entities(text_ins_telephone)
            for document in resp.documents:
                for entity in document.entities:
                    if entity.type in 'Phone_Number':
                        self.info['Telephone']=entity.name
        return self.info
    # func to extract insured name 
    
    def ins_policy_num(self,text):
        # regex to extract for patient name 
        rem='\(.*\)'
        reg_name='INSURED\'S POLICY GROUP' # haven't used yet , check later for use
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
        text=text.replace(',','')
    #     print(text)
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if (entity.type in 'Quantity'):# or entity.sub_type in 'Number':
                    self.info['Insured\'s policy number']=entity.name
#        print(entity.sub_type in 'Number')
        return self.info
    
    # func to extract amount paid
    def amt_paid(self,text):
        rem='\(.*\)'
        reg_name='AMOUNT PAID'
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
    #     print(text)
        # get text for amount paid
        to_remove=find_pattern(text,reg_name)
        if to_remove!=False:
            text_amt=text[to_remove.span()[0]:]
            print(text_amt)
            resp=extract_entities(text_amt)
            for document in resp.documents:
                for entity in document.entities:
                    if (entity.type in 'Quantity'):# or entity.sub_type in 'Number':
                        self.info['amount paid']=entity.name
        return self.info 
        
      # func to extract federal tax id number
    def federal_id(self,text):
        rem='\(.*\)'
        reg_name='FEDERAL TAX'
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
    #     print(text)
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if (entity.type in 'Quantity'):# or entity.sub_type in 'Number':
                    self.info['federal id']=entity.name
        return self.info     
    
    #func to extract total charge
    def total_chg(self,text):
        reg_name='TOTAL CHARGE .{1,5}[0-9]*'
        reg_amt='$'
        to_remove=find_pattern(text,reg_name)# find amount in text
        text_amt=to_remove.group()
        resp=extract_entities(text_amt)
        for document in resp.documents:
            for entity in document.entities:
                if (entity.type in 'Quantity'):
                    self.info['total charge']=entity.name
        
        return self.info
    # func to extract Id. qual
    def qual(self,text):
        reg_qual='QUAL'
        # use key phrase to extract entites
        reg_zz='zz'
        i=0
        for match in re.finditer(reg_zz,text):
            self.info['ID.Qual'+str(i)+'.']=text[match.start():match.end()]
            i+=1
        return self.info
                
    # func to extract rendering provider ID
    def render(self,text):
        reg_render='RENDERING.*PROVIDER'
        r=find_pattern(text,reg_render)
        text_render=text[r.span()[0]:]
        # making regex to find render number assuming that it has 8 digit number
        find_render='[0-9]{10}'
        i=0
        for match in re.finditer(find_render,text_render):
            self.info['rendering provider id '+str(i)+'.']=text_render[match.start():match.end()]
            i+=1
        return self.info    
    
    # func to extract insured I.D number
    def insured_id(self,text):
        rem='\(.*\)'
        reg_name='INSURED.*NUMBER'
        to_remove=find_pattern(text,rem)
        if to_remove!=False:
            text=text[0:to_remove.span()[0]]+text[to_remove.span()[1]+1:]
    #     print(text)
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if (entity.type in 'Quantity'):
                    self.info['Insured I.D number']=entity.name
        return self.info

    # func to extract company name and address
    def comp_details(self,text):
        reg='BLU.*CROSS.*BLUE'
#        r=find_pattern(text,reg)
        text=text.replace(',','')
    #     print(text)
#        text_comp=text[r.span()[0]:]
        # remove 
        resp=extract_entities(text)
        for document in resp.documents:
            for entity in document.entities:
                if (entity.type in 'Organization'):
                    self.info['Company name']=entity.name
                if (entity.type in 'Location'):
                    self.info['Company Address ']=entity.name
        return self.info
    # extract the CPT/HCPCS 
    def hcpcs(self,text):
        reg='CPT/HCP'
        r=find_pattern(text,reg)
        text_cpt=text[r.span()[0]:]
        reg_num='[0-9]{5}'
        i=0
        for match in re.finditer(reg_num,text_cpt):
            self.info['CPT/HCPCS '+str(i)+'.']=text_cpt[match.start():match.end()]
            i+=1
        return self.info
    def get_entites(self,text_new):
        for t in text_new:
#     print(t)
            if find_pattern(t,self.reg_pt_name):
                if not self.info.get('Patients Name',False):
                    # call patient name func
                    self.pt_name(t)
                else:
                    print("patient name is already present")
            elif find_pattern(t,self.reg_ins_name):
                if not self.info.get("Insured's Name",False):
                    # call insured name func
                    self.ins_name(t)
                else:
                    print("insured name is already present")
                    
            elif find_pattern(t,self.reg_ins_add):
                if not self.info.get("City",False):
                    # call ins add func
                    self.ins_add(t)
                else:
                    print("city name is already present")
            elif find_pattern(t,self.reg_ins_policy):
                if not self.info.get("Insured's policy number",False):
                    self.ins_policy_num(t)
                else:
                    print("insured policy number is already present")
            if find_pattern(t,self.reg_amt):
                if not self.info.get("amount paid",False):
                    self.amt_paid(t)
                else:
                    print("amt is already present")
            if find_pattern(t,self.reg_charge):
                if not self.info.get('total charge',False):
                    self.total_chg(t)
                else:
                    print('total charge is already present')
            if find_pattern(t,self.reg_qual):
                if not self.info.get('ID.Qual0.',False):
                    self.qual(t)
                else:
                    print("qual id is already present")
            if find_pattern(t,self.reg_render):
                if not self.info.get("rendering provider id 0.",False):
                    self.render(t)
                else:
                    print("rendering id is already present")
            if find_pattern(t,self.reg_ins_num):
                if not self.info.get("Insured I.D number",False):
                    self.insured_id(t)
                else:
                    print("insured id number is already present")
            if find_pattern(t,self.reg_comp_name):
                if not self.info.get("Company name",False):
                    self.comp_details(t)
                else:
                    print("company details is already present")
            if find_pattern(t,self.reg_comp_add):
                if not self.info.get("CPT/HCPCS 0.",False):
                    self.hcpcs(t)
                else:
                    print("cpt/hcpcs details is already present")
            if find_pattern(t,self.reg_federal):
                if not self.info.get("federal id",False):
                    self.federal_id(t)
                else:
                    print("federal id already present")

def text_cleaning(text_new):
    for t in range(len(text_new)):
    # first remove all content in brackets
        reg_bracket='\(.*?\)'
#     if find_pattern(text_new[t],reg_bracket):
        for match in re.finditer(reg_bracket,text_new[t]):
            print(text_new[t][match.start():match.end()])
            print(match.group())
            text_new[t]=text_new[t].replace(match.group(),'')
#             text_new[t]=text_new[t][:match.start()-1]+text_new[t][match.end()+1:]
        reg_1='HEALTH.*INSURANCE.*CLAIM.*COMMITTEE|SIGNATURE.*OF.*PHYSICIAN.*'
#         reg_2='SIGNATURE.*OF.*PHYSICIAN.*'
        if find_pattern(text_new[t],reg_1):
            r=find_pattern(text_new[t],reg_1)
            text_new[t]=text_new[t].replace(r.group(),"")
            
    return text_new

if __name__=="__main__":
#     filename="HCFA 1500 form.pdf"
#     pdf_to_png(filename)
    # object for textual data from image
    data=requests.get('https://imagecleaningpreprocesso.blob.core.windows.net/sendtoaiapiblob/9053507b-f038-4d4f-bbf1-75c6354a4018')
    texual_data=ocr_extraction()
#     image_path="HCFA_1500_1.png"
#     image_data=open(image_path,"rb").read()
    text=texual_data.text_extract(data)
#    text_new=" ".join(text)
#    
#    text_new=re.split('[0-9]{1,2}\.| [a-z]{1}\.',text_new)
    # func 
    text_new=text_cleaning(text)
    print(text_new)
#     object for entity mapping
    entity_mapping=entity_extraction()
    print("before extraction",entity_mapping.info)
    entity_mapping.get_entites(text_new)
    print("after extraction",entity_mapping.info)
else :
    print("this file is being imported")

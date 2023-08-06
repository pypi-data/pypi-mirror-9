#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apiclient import errors
from apiclient import http
from apiclient.http import MediaIoBaseDownload
from apiclient.http import HttpRequest
from base import GDBase
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from gdcmdtools.auth import GDAuth

import requests
import re
import os
import json

import io

import pprint

export_format = {
    "application/vnd.google-apps.spreadsheet":["pdf", "ods", "xlsx"],
    "application/vnd.google-apps.document":["pdf", "docx", "rtf", "odt", "html", "txt"],    
    "application/vnd.google-apps.presentation":["pdf", "pptx", "txt"],
    "application/vnd.google-apps.drawing":["png", "pdf", "jpeg", "svg"],
    "application/vnd.google-apps.script+json":["json"],
    }

""" application/vnd.google-apps.script+json
{  
    "files": [  
        {  
            "id": "bbda34aa-c700-48d9-88bd-ad2573a0620a",  
            "name": "Code",  
            "source": "FILE CONTENT",
            "type": "server_js"
        }
    ]
}


"""

class GDGet:
    def __init__(self, file_id, format, save_as):
        # base
        auth = GDAuth()
        creds = auth.get_credentials()
        if creds == None:
            raise Exception("Failed to retrieve credentials")

        self.http = auth.get_authorized_http()

        base = GDBase()
        self.service = base.get_drive_service(self.http)
        
        self.file_id = file_id
        self.format = format

        if save_as == None:
            self.save_as = None
        else:
            self.save_as = os.path.abspath(save_as)
 
    def parse_gas_json(self, file_content, save_as):
        map_type_ext = {"server_js":"js", "html":"html"}
        try:
            jsons = json.loads(file_content)
            new_json = {"files":[]}
            for j in jsons["files"]:
                file_id = j["id"]
                file_name = j["name"]
                file_source = j["source"]
                file_type = j["type"]

                if file_type in map_type_ext.keys():
                    file_ext = map_type_ext[file_type]
                else:
                    file_ext = file_type

                file_fullname = "%s.%s" % (file_name, file_ext) 

                with open(file_fullname, 'wb+') as f:
                    f.write(file_source)
                
                j.pop("source")
                new_json["files"].append(j)

            # save the project id, we need the id to upload project
            new_json["id"] = self.file_id
            with open(save_as, 'wb+') as f:
                f.write(json.dumps(new_json, indent=4))

        except Exception, e:  
            logger.error(e)
            raise

    def run(self):
        try: 
            service_response = self.get()

            result_title_format = self.get_title_format(service_response)
            logger.debug(result_title_format)

            #self.get_by_media()
        
            #return 

            title, return_format = result_title_format
            if self.format != "raw":
                title = title +"." +self.format

            if self.format not in return_format.keys():
                raise Exception("The specified format \'%s\' is not allowed, available format are \"%s\", please correct option: --export_format" % (self.format, ', '.join(return_format.keys())))

            file_content = self.get_by_format(return_format[self.format])

            if self.save_as == None:
               self.save_as = title 

            if self.format == "json":
                self.parse_gas_json(file_content, self.save_as)               
            else:
                with open(self.save_as, 'wb+') as f:
                    f.write(file_content)

        except Exception, e:
            logger.error(e)
            raise

        return return_format


    def get(self):
        try:
            response = self.service.files().get(fileId=self.file_id).execute()
            logger.debug(pprint.pformat(response))
            return response

        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)
        return None

    def get_by_media(self):
        local_fd = io.FileIO('/tmp/c', mode='wb')
        request = self.service.files().get_media(fileId=self.file_id)
        media_request = http.MediaIoBaseDownload(local_fd, request)

        while True:
            try:
                download_progress, done = media_request.next_chunk(num_retries=30)
            except errors.HttpError, error:
                logger.debug('An error occurred: %s' % error)
                return
            if download_progress:
                logger.debug('Download Progress: %.2f%%' % int(download_progress.progress() * 100))
            if done:
                logger.debug('Download Complete')
                return


    def get_title_format(self, service_response):
        export_links = service_response.get('exportLinks', None)
        return_format = {}

        title = service_response.get('title',None)

        
        logger.debug(title)
        logger.debug(export_links)

        if export_links == None:
            download_link = service_response.get(u'downloadUrl', None)
            return_format["raw"] = download_link
        else:
            export_link_values = export_links.values()

            if len(export_link_values) > 0 :
                for link in export_link_values:
                    m = re.match(r'^.*[Ff]ormat=(.*)$',link)
                    return_format[m.group(1)] = link

        return title, return_format

    #def get_oauth2_token(self):
    def get_by_format(self,link):
        token_url = "https://accounts.google.com/o/oauth2/token"
        scope=[
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/fusiontables',
        'https://www.googleapis.com/auth/drive.scripts'
        ]
        scopex = ["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile"]
        from requests_oauthlib import OAuth2Session
        client_id = "81300559691-su4pttgfjbkhjhi1nlcbbf61nn2p9m7s.apps.googleusercontent.com"
        token = {"access_token": "ya29.OwGXi0Cqp_UDi5vvub1qYpMUKfQ6rvNa-lrHgaLuQUjT31VD-dd1sekf6K1ULBSpFkn7Kr1HjAS0Xg", "token_type": "Bearer", "expires_in": 3600}

        client_secret = "xOMEW84ysS9Wm8orSQTMZx6L"
        google = OAuth2Session(client_id, scope=scope,token=token)
        
        #link="https://docs.google.com/feeds/download/documents/export/Export?id=1Pzl-Jw9vxdfXUCnr4hcemv23mYfBJibztwmeVQP2Mok&exportFormat=pdf"
        #google.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_response)
        #r = google.get('https://www.googleapis.com/drive/v2/files')
        local_filename="/opt/tmp/yy"
        r = google.get(link, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): 
                if chunk: # filter out keep-alive new chunks
                    logger.debug("ok")
                    f.write(chunk)
                    f.flush()

    def requests_oauth2(self):
        google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

    def get_by_formatgg1(self, link):
        resp, content = self.service._http.request(link)

        if resp.status == 200:
          logger.debug('Status: %s' % resp)
          return content
        else:
          logger.error('An error occurred: %s' % resp)
          return None       

    def get_by_format2(self, link):
        #resp, content = self.service._http.request(link)

        fh = io.FileIO('cow.png', mode='wb')

        downloader = MediaIoBaseDownload(fh, self.service._http.request, chunksize=1024*1024)

        if resp.status == 200:
          logger.debug('Status: %s' % resp)
          return content
        else:
          logger.error('An error occurred: %s' % resp)
          return None

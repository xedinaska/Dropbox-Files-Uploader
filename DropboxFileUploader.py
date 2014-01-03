# -*- coding: utf-8 -*- from __future__ import unicode_literals

from dropbox import client as dropboxClient
from dropbox import rest
from os import path
from Tkinter import *
import sys


class DropboxFileUploader:

    app_key = ''
    app_secret = ''
    access_token = None
    client = None
    flow = None

    def regenerateAccessToken(self):
        authorizeURL = self.getAuthorizeURL()
        self.getAuthorizeCode(authorizeURL)

    def getAuthorizeURL(self):
        self.flow = dropboxClient.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorizeUrl = self.flow.start()
        return authorizeUrl

    def getAccessTokenByAuthorizeCode(self, code):
        accessToken, userId = self.flow.finish(code)
        return accessToken

    def getAuthorizeCode(self, authorizeUrl):

        root = Tk(className="Dropbox Access Message")

        def getAuthorizeCodeFromTextWidget():
            code = entry.get()
            root.destroy()
            accessToken = self.getAccessTokenByAuthorizeCode(code)
            file = open('token.txt', 'w')
            file.write(accessToken)
            file.close()
            self.initDropboxClientObject(accessToken)

        def openUrl(url):
            import webbrowser
            webbrowser.open(url)

        label = Label(root, text="Please open link: " + authorizeUrl + " and paste code bellow", font="Arial 14")
        entry = Entry(root, width=50)
        button = Button(root, text="Submit", command=getAuthorizeCodeFromTextWidget)

        label.grid(row=0, column=0)
        entry.grid(row=1, column=0, pady=20)
        button.grid(row=2, column=0, pady=5)

        label.bind("<Button-1>", lambda e, url=authorizeUrl: openUrl(authorizeUrl))

        root.mainloop()

    def initDropboxClientObject(self, access_token):
        try:
            self.client = dropboxClient.DropboxClient(access_token)
        except ValueError:
            #if access_token is empty
            self.regenerateAccessToken()

    def upload(self, filePath):
        filename = path.basename(filePath)
        try:
            f = open(filePath)
            file = self.client.put_file(filename, f)
        except rest.ErrorResponse:
            #client object corrupted - access token expired (?)
            #try to get new access token and re-initialize client object
            self.regenerateAccessToken()
            f = open(filePath)
            file = self.client.put_file(filename, f)

        f.close()
        return self.getUploadedFileLink(file['path'])

    def getUploadedFileLink(self, filename):
        response = self.client.share(filename)
        return response['url']

    def uploadFileAndGetUploadedFileLink(self, filePath):
        self.initDropboxClientObject(self.loadAccessTokenFromFile())
        return self.upload(filePath)

    def loadAccessTokenFromFile(self):
        try:
            file = open('token.txt', 'rw')
            file.close()
        except IOError:
            #create file if not exist
            createdFile = open('token.txt', 'w')
            createdFile.close()
        file = open('token.txt', 'rw')
        access_token = file.read()
        file.close()
        return access_token


dboxFileUploader = DropboxFileUploader()

filePath = ' '.join(sys.argv[1:]).replace('\'', '')

import logging
logging.basicConfig(level=logging.DEBUG, filename='error.txt')

try:
    if path.exists(filePath):
        url = dboxFileUploader.uploadFileAndGetUploadedFileLink(filePath)
        print(url)
    else:
        logging.exception("Oops:")
        print('error')
except:
    logging.exception("Oops:")

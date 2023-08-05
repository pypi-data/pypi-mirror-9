#!/usr/bin/env python
from __future__ import print_function

import os
import re

import boto
from boto.s3.connection import S3Connection
from boto.iam.connection import IAMConnection
import inquirer

key_policy_json = """{
  "Statement": [
    {
      "Action": "iam:*AccessKey*",
      "Effect": "Allow",
      "Resource": "%s"
    }
  ]
}"""

user_bucket_policy_json = """{
  "Statement": [
    {
    "Effect": "Allow",
    "Action": %s,
    "Resource": [
      "arn:aws:s3:::%s",
      "arn:aws:s3:::%s/*"
    ]
  },
  {
    "Effect": "Deny",
    "Action": ["s3:*"],
    "NotResource": [
      "arn:aws:s3:::%s",
      "arn:aws:s3:::%s/*"
    ]
  }]}"""

public_read_bucket_policy = """{
  "Statement":[{
    "Sid":"AllowPublicRead",
      "Effect":"Allow",
      "Principal": {
            "AWS": "*"
         },
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::%s/*"
      ]
  }]}"""

questions = [
    inquirer.Text('bucket_name',
                  message='Bucket Name to create',
                  validate=lambda _, x: re.match('[a-z0-9]+', x),
                  ),
    inquirer.Text('username',
                  message='Username to create',
                  validate=lambda _, value: re.match('[a-z0-9]+', value),
                  ),
    inquirer.List('acl',
                  message='Choose ACL Policy for this user',
                  choices=['read-only', 'all']
                  ),
    inquirer.List('public',
                  message='Should this bucket be readable by public',
                  choices=['Yes', 'No']
                  )
    ]


def s3_bucket_maker(answers):
    access_key = os.environ['ACCESS_KEY_ID']
    secret_key = os.environ['SECRET_ACCESS_KEY']
    s3conn = S3Connection(access_key, secret_key)
    iamconn = IAMConnection(access_key, secret_key)

    bucket = s3conn.create_bucket(answers['bucket_name'])

    print("BUCKET: %s created" % answers['bucket_name'])

    user = None
    try:
        user = iamconn.get_user(answers['username'])
    except boto.exception.BotoServerError, e:
        if e.status == 404:
            print('User not found... creating one')
            user = iamconn.create_user(answers['username'])
            keys = iamconn.create_access_key(answers['username'])
            print(keys)
        else:
            raise e
    print(user)

    policy = key_policy_json % (user.arn)
    iamconn.put_user_policy(answers['username'], 'UserKeyPolicy', policy)

    actions = "[\"s3:*\"]"
    if (answers['acl'] == 'read-only'):
        actions = "[\"s3:ListBucket\",\"s3:GetObject\",\"s3:GetObjectVersion\"]"
    policy = user_bucket_policy_json % (actions, answers['bucket_name'], answers['bucket_name'], answers['bucket_name'], answers['bucket_name'])
    iamconn.put_user_policy(answers['username'], 'UserS3Policy', policy)

    if (answers['public'] == 'Yes'):
        bucket.set_policy(public_read_bucket_policy % answers['bucket_name'])


def main():
    inq = inquirer.prompt(questions)
    s3_bucket_maker(inq)

#!/usr/bin/env python3

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': '<h1>Hello from Netlify Function!</h1><p>This is a test function to verify Python function detection.</p>'
    } 
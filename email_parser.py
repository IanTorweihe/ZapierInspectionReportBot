#import statements 
import re
from urllib.request import urlopen
from html.parser import HTMLParser

def extract_msg_data(emailBody):
  """
  Parse a email body and extract report URL and other information. It then 
  sends an HTTP GET request to that URL to retrieve its content, which is 
  parsed using an HTML parser to extract a document download URL. The download URL 
  is then concatenated with a fixed prefix to form a complete URL, which is 
  included in a dictionary along with the original URL. The resulting 
  dictionary is returned as the output of the script.

  input: email body as string 
  output: dictionary containing direct download url for pdf, url 
          of inspection page, and report number parsed from email.
  """
  class MyHTMLParser(HTMLParser):
      def __init__(self):
          super().__init__()
          self.download_url = None
  
      def handle_starttag(self, tag, attrs):
          if tag == 'a' and ('title', 'Download') in attrs:
              for name, value in attrs:
                  if name == 'href':
                      self.download_url = value
  
  #EXTRACT REPORT URL FROM EMAIL BODY
  #create regex object for report url search
  #inspectionwebsite should be replaced with specific url
  pattern = re.compile(r'https://www\.inspectionwebsite\.com/Document/Details/.*?\n')
  #search email body for doc url and return match object
  matchURL = re.search(pattern, emailBody)
  matchURL = matchURL.group(0).strip() if matchURL else ""
  
  #EXTRACT REPORT FIELD FROM EMAIL BODY
  # split the text into sections using the dash separator.
  # Note: This is specific to the format of notification emails
  sections = emailBody.split('------------------------------------------------------------------------------')
  
  #DEBUG - Print statements 
  """
  print(sections[2])
  """
  
  # if there is more than one section, the second section will contain the report section
  if len(sections) > 1:
      report_section = sections[2]
  
      # search for the first occurrence of a pattern that matches a hyphen followed
      # by one or more non-hyphen characters, followed by another hyphen, within the
      # captured section
      report_match = re.search(r"(?<=- ).+?(?= -)", report_section, re.DOTALL)
  
      # if a match was found, extract the contents of the capturing group
      report_number = "report_number error"
      if report_match:
          report_number = report_match.group(0)
  
  
  # create dictionary object to return for report page url AND report number
  output = [{'pageURL': matchURL, 'reportNum': report_number}]
  
  # url to inspection report page parsed from email
  url = matchURL
  
  # Send an HTTP GET request to the URL and get the response
  response = urlopen(url)
  
  # Use HTMLParser to parse the HTML content of the response
  parser = MyHTMLParser()
  parser.feed(response.read().decode('utf-8'))
  
  # Get the direct document download URL
  download_url = parser.download_url
  # Replace "inspectionwebsite"
  prefix = "https://www.inspectionwebsite.com"
  
  # concatenate with url prefix
  download_url = prefix + download_url
  
  output = [{'pageURL': matchURL, 'reportNum': report_number, 'downloadURL' : download_url}]
  
  return output
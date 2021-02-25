import requests
from requests.exceptions import Timeout
import re
from bs4 import BeautifulSoup
import glob
from smart_open import open as _Open

from px_aux import saveFile as _saveFile
from aux_build import SCRAPPED_PAGES_FOLDER as _SCRAPPED_PAGES_FOLDER, HTML_PAGES_FOLDER as _HTML_PAGES_FOLDER

class scrapFunctions():

	# Download HTML pages
	def downloadPage(self, page):
		# Make the request
		try:
			request = requests.get(page, timeout=10)
		except Timeout as e:
			print("*** Request Exception (Timeout): ", page)
			raise Exception("Timeout")
		except Exception as e:
			print("*** Request Exception ("+str(e)+"): " + page)
			raise Exception("Unknown")

		# Extract HTML from Response object and print
		try:
			html = request.text
		except Exception as e:
			print("*** HTML Exception ("+str(e)+"): " + page)
			raise Exception("Unknown")

		return html


	# Scrap HTML pages
	def extractTextFromHTML(self, page):

		try:
			html = self.downloadPage(page)
		except Exception as e:
			print("*** extractTextFromHTML Exception: "+str(e))
			raise Exception(str(e))

		cleanedText = ""

		# Create a BeautifulSoup object from the HTML
		try:
			soup = BeautifulSoup(html, "html5lib")
		except Exception as e:
			print("*** extractTextFromHTML Exception: "+str(e))
			raise Exception(str(e))


		# Scrap plain text from paragraphs
		try:
			# Extract all paragraphs
			for p in soup.find_all("p"):
				# Clean paragraphs
				plainParagraph = p.get_text()

				# Remove references from text
				plainParagraph = re.sub("([\[]).*?([\]])", "", plainParagraph)
				# print(plainParagraph)

				# Append cleaned paragraph to cleanedText
				# Separate paragraphs by break lines
				cleanedText += plainParagraph + "\n"

		except Exception as e:
			print("*** extractTextFromHTML (extracting p): "+str(e))
			raise Exception(str(e))

		return cleanedText





	# Scrap HTML pages
	def scrapPage(self, page):
		# Make the request
		try:
			request = requests.get(page, timeout=10)
		except Timeout as e:
			print("*** Timeout ***", page)
			raise Exception("Timeout")
		except:
			print("scrapPage: Connection broken: " + page)
			return ""


		# Extract HTML from Response object and print
		try:
			html = request.text
		except Exception as e:
			print("scrapPage (text): " + str(e))
			return ""

		# Create a BeautifulSoup object from the HTML
		try:
			soup = BeautifulSoup(html, "html5lib")
		except Exception as e:
			print("scrapPage (BeautifulSoup): " + str(e))
			return ""

		try:
			# Get the page title
			pageTitle = soup.title.string
			# Create a page name from the page title after removing special characters
			pageName = pageTitle.translate ({ord(c): "-" for c in "!@#$%^*()[]{};:,./<>?\|`=+"})
		except Exception as e:
			print("scrapPage (title.string): " + str(e))


		# remove the footer div
		try:
			soup.find('footer', id="footer").decompose()
		except Exception as e:
			print("scrapPage (footer): "+str(e))

		# remove the mw-navigation div
		try:
			soup.find('div', id="mw-navigation").decompose()
		except Exception as e:
			print("scrapPage (div mw-navigation): "+str(e))

		# remove navigation links
		try:
			for link in soup.find_all("a", {'class': 'mw-jump-link'}):
				link.decompose()
		except Exception as e:
			print("scrapPage (a): "+str(e))

		# remove navigation sections (Includes the head and the side panel)
		try:
			for link in soup.find_all("div", {'role': 'navigation'}):
				link.decompose()
		except Exception as e:
			print("scrapPage (no navigation sections found): "+str(e))

		# Other elements that can be removed:
		# Site notices: div with id = "siteNotice"
		# References


		# remove the css
		try:
			soup.style.decompose()
		except Exception as e:
			print("scrapPage (no style): "+str(e))


		# remove all the js tags
		try:
			for tag in soup.find_all("script"):
				tag.decompose()
		except Exception as e:
			print("scrapPage (no script): "+str(e))


		# Extract text from HTML
		try:
			text = soup.get_text()
		except Exception as e:
			print("scrapPage (get_text): "+str(e))
			return ""

		# Since we don't need the whole page components, it would be better to extract..
		# ..the text only from paragraphs. This works for wikipedia pages.
		# Scrapping the whole page now is not necessary, but I left it just in case needed later

		# To save all paragraphs
		cleanedText = ""


		# Scrap plain text from paragraphs
		try:
			# Extract all paragraphs
			for p in soup.find_all("p"):
				# Clean paragraphs
				plainParagraph = p.get_text()

				# Remove references from text
				plainParagraph = re.sub("([\[]).*?([\]])", "", plainParagraph)
				# print(plainParagraph)

				# Append cleaned paragraph to cleanedText
				# Separate paragraphs by break lines
				cleanedText += plainParagraph + "\n"

		except Exception as e:
			print("scrapPage (extracting p): "+str(e))

		return cleanedText




	# Takes a url and saves it to html file, and returns the html content
	def urlToHtml(self, url):
		# Make the request
		try:
			request = requests.get(url)
		except:
			print("connection broken: " + url)
			return


		# Extract HTML from Response object and print
		html = request.text

		# Create a BeautifulSoup object from the HTML
		soup = BeautifulSoup(html, "html5lib")

		# Get the page title
		pageTitle = soup.title.string

		# Create a page name from the page title after removing special characters
		pageName = pageTitle.translate ({ord(c): "-" for c in "!@#$%^*()[]{};:,./<>?\|`=+"})

		# Add file extension for saving pages
		fileName = pageName + ".html"

		# Save to html file
		_saveFile(_HTML_PAGES_FOLDER+fileName, html)

		return html


	# Takes a url and saves it to text file, and returns the page name and the cleaned text
	def urlToText(self, url):
		# Make the request
		try:
			request = requests.get(url)
		except:
			print("connection broken: " + url)
			return


		# Extract HTML from Response object and print
		html = request.text

		# Create a BeautifulSoup object from the HTML
		soup = BeautifulSoup(html, "html5lib")

		# Get the page title
		pageTitle = soup.title.string

		# Create a page name from the page title after removing special characters
		pageName = pageTitle.translate ({ord(c): "-" for c in "!@#$%^*()[]{};:,./<>?\|`=+"})

		# remove the footer div
		try:
			soup.find('div', id="footer").decompose()
		except Exception:
			print("not a wikipedia page")

		# remove the mw-navigation div
		try:
			soup.find('div', id="mw-navigation").decompose()
		except Exception:
			print("not a wikipedia page")

		# remove navigation links
		try:
			for link in soup.find_all("a", {'class': 'mw-jump-link'}):
				link.decompose()
		except Exception:
			print("not a wikipedia page")

		# remove navigation sections (Includes the head and the side panel)
		try:
			for link in soup.find_all("div", {'role': 'navigation'}):
				link.decompose()
		except Exception:
			print("no navigation sections found")

		# Other elements that can be removed:
		# Site notices: div with id = "siteNotice"
		# References


		# remove the css
		try:
			soup.style.decompose()
		except Exception:
			pass


		# remove all the js tags
		try:
			for tag in soup.find_all("script"):
				tag.decompose()
		except Exception:
			pass


		# Extract text from HTML
		text = soup.get_text()

		# Since we don't need the whole page components, it would be better to extract..
		# ..the text only from paragraphs. This works for wikipedia pages.
		# Scrapping the whole page now is not necessary, but I left it just in case needed later

		# To save all paragraphs
		cleanedText = ""


		# Scrap plain text from paragraphs
		try:
			# Extract all paragraphs
			for p in soup.find_all("p"):
				# Clean paragraphs
				plainParagraph = p.get_text()

				# Remove references from text
				plainParagraph = re.sub("([\[]).*?([\]])", "", plainParagraph)
				# print(plainParagraph)

				# Append cleaned paragraph to cleanedText
				# Separate paragraphs by break lines
				cleanedText += plainParagraph + "\n"

		except Exception:
			pass


		# Add file extension for saving pages
		fileName = 	pageName + ".txt"

		# Save to html file
		_saveFile(_SCRAPPED_PAGES_FOLDER+fileName, html)

		return pageName, cleanedText


	# Takes html and saves it to text file, and returns the page name and the cleaned text
	def htmlToText(self, html):
		# Create a BeautifulSoup object from the HTML
		soup = BeautifulSoup(html, "html5lib")

		# Get the page title
		pageTitle = soup.title.string

		# Create a page name from the page title after removing special characters
		pageName = pageTitle.translate ({ord(c): "-" for c in "!@#$%^*()[]{};:,./<>?\|`=+"})

		# remove the footer div
		try:
			soup.find('div', id="footer").decompose()
		except Exception:
			print("not a wikipedia page")

		# remove the mw-navigation div
		try:
			soup.find('div', id="mw-navigation").decompose()
		except Exception:
			print("not a wikipedia page")

		# remove navigation links
		try:
			for link in soup.find_all("a", {'class': 'mw-jump-link'}):
				link.decompose()
		except Exception:
			print("not a wikipedia page")

		# remove navigation sections (Includes the head and the side panel)
		try:
			for link in soup.find_all("div", {'role': 'navigation'}):
				link.decompose()
		except Exception:
			print("no navigation sections found")

		# Other elements that can be removed:
		# Site notices: div with id = "siteNotice"
		# References


		# remove the css
		try:
			soup.style.decompose()
		except Exception:
			pass


		# remove all the js tags
		try:
			for tag in soup.find_all("script"):
				tag.decompose()
		except Exception:
			pass


		# Extract text from HTML
		text = soup.get_text()

		# Since we don't need the whole page components, it would be better to extract..
		# ..the text only from paragraphs. This works for wikipedia pages.
		# Scrapping the whole page now is not necessary, but I left it just in case needed later

		# To save all paragraphs
		cleanedText = ""


		# Scrap plain text from paragraphs
		try:
			# Extract all paragraphs
			for p in soup.find_all("p"):
				# Clean paragraphs
				plainParagraph = p.get_text()

				# Remove references from text
				plainParagraph = re.sub("([\[]).*?([\]])", "", plainParagraph)
				# print(plainParagraph)

				# Append cleaned paragraph to cleanedText
				# Separate paragraphs by break lines
				cleanedText += plainParagraph + "\n"

		except Exception:
			pass


		# Add file extension for saving pages
		fileName = 	pageName + ".txt"

		# Save to html file
		_saveFile(_SCRAPPED_PAGES_FOLDER+fileName, html)

		return pageName, cleanedText


	# Takes a list of urls and saves them to html files
	def urlListToHtml(self, urlsList):
		for url in urlsList:

			# Retrieves the page title and the scraped page content
			try:
				pageName, pageContent = urlToHtml(url)

			except Exception as e:
				print("Error retrieving page: " + e)
				unretrieved_pages.append(page)
				continue


	# Takes a folder path i.e.: htmlFolder/, and scraps all pages
	def htmlFolderToText(self, folderPath):
		list_of_files = glob.glob(folderPath+"*.html")

		for html_file in list_of_files:
			file = _Open(html_file, "r")
			html = file.read()

			pageName, cleanedText = htmlToText(html)

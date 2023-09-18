# find-apps-eligible-for-automated-patching
Find applications installed in your mac environment that can be patched automatically using a "set and forget" method with Jamf App Installers or Installomator.

## Purpose
Patching for 3rd-party software can be automated using [Jamf App Installers](https://learn.jamf.com/bundle/jamf-app-catalog/page/App_Installers_Software_Titles.html) and/or [Installomator](https://github.com/Installomator/Installomator). This script is designed to help you discover which apps installed in your mac environment are eligible for patching via these methods. New software titles are added to the Jamf App Installers and Installomator projects often

## Usage
- Download the script
- Replace JAMF_URL with your actual Jamf Pro Server URL
- Replace API_Token with your actual Jamf Pro API Bearer Token
- Make the script executable `chmod +x /path/to/script.py`
- Run the script in terminal

## Notes
- Some of the software titles listed on the Jamf App Installers FAQ page have names that are different than the actual title that gets returned from the Jamf API, this causes them to not appear in the final list returned by the script (Ex. Microsoft Outlook is listed as "Microsoft Outlook 365" on the FAQ page but listed as just "Microsoft Outlook" in Jamf).
- Just because patching for an application _can_ be automated does not always mean that it _should_ be automated. Always make sure that the patching process for applications in your environment is in line with the desired user experience, change management protocols, and security recommendations. 

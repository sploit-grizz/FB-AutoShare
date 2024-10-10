from flask import Flask, request, render_template, jsonify
import os, re, requests, datetime, random

app = Flask(__name__)

# Map of month numbers to names
FR = {'1': 'january', '2': 'february', '3': 'march', '4': 'april', '5': 'may',
      '6': 'june', '7': 'july', '8': 'august', '9': 'september', '10': 'october',
      '11': 'november', '12': 'december'}

# Date formatting
tgl = datetime.datetime.now().day
bln = FR[str(datetime.datetime.now().month)]
thn = datetime.datetime.now().year
sekarang = f"{tgl} {bln} {thn}"

# Load the main page
@app.route('/')
def index():
    return render_template('index.html')

# Handle the sharing process via POST request
@app.route('/share', methods=['POST'])
def share():
    try:
        data = request.get_json()
        cookie = data.get('cookie')
        url = data.get('url')
        try:
            limit = int(data.get('limit', 1))  # Handle limit safely
        except ValueError:
            return jsonify({"error": "Limit must be an integer."}), 400
        
        headers = {
            "authority": "graph.facebook.com",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/98.0.4758.66 Safari/537.36"
        }
        
        session = requests.Session()
        token = get_token(cookie)
        
        if not token:
            return jsonify({"error": "Invalid or expired cookie."}), 400
        
        results = []
        
        for _ in range(limit):
            response = session.post(
                f"https://graph.facebook.com/me/feed?link={url}&published=0&access_token={token}",
                headers=headers, cookies={"cookie": cookie}
            ).json()
            
            if "id" in response:
                results.append({"status": "success", "post_id": response['id']})
            elif "error" in response:
                results.append({"status": "failed", "reason": response['error']['message']})
            else:
                results.append({"status": "failed", "reason": "Unknown error"})
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_token(cookie):
    try:
        response = requests.get(
            "https://business.facebook.com/business_locations",
            headers={
                "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.011) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.86 "
                              "Mobile Safari/537.36",
                "cookie": cookie
            }
        )
        match = re.search("(EAAG\w+)", response.text)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None


if __name__ == '__main__':
    import os
    
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
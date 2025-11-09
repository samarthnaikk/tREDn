import requests
import json
import csv
import os
from datetime import datetime
from urllib.parse import quote
import time
from io import StringIO

class RedditUtils:
    def __init__(self, data_directory="data"):
        self.base_url = "https://www.reddit.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.data_dir = data_directory
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_reddit_data(self, query, sort_method="top", time_period="month", post_limit=25):
        search_url = f"https://www.reddit.com/search.json?q={quote(query)}"
        
        try:
            print(f"Fetching from: {search_url}")
            response = requests.get(search_url, headers=self.headers)
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"Data keys: {list(data.keys()) if data else 'None'}")
            if data and 'data' in data:
                print(f"Posts found: {len(data['data']['children'])}")
            time.sleep(1.2)
            return data
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Other error: {e}")
            return None
    
    def fetch_post_comments(self, subreddit_name, post_identifier):
        comments_url = f"{self.base_url}/r/{subreddit_name}/comments/{post_identifier}.json"
        
        try:
            response = requests.get(comments_url, headers=self.headers, params={"raw_json": 1})
            response.raise_for_status()
            time.sleep(1.2)
            return response.json()
        except requests.RequestException as e:
            print(f"Comment fetch error: {e}")
            return None
    
    def extract_post_data(self, raw_post_data):
        return {
            "title": raw_post_data.get("title", ""),
            "author": raw_post_data.get("author", "unknown"),
            "subreddit": raw_post_data.get("subreddit", ""),
            "external_url": raw_post_data.get("url", ""),
            "reddit_permalink": f"{self.base_url}{raw_post_data.get('permalink', '')}",
            "score": raw_post_data.get("score", 0),
            "upvotes": raw_post_data.get("ups", 0),
            "comment_count": raw_post_data.get("num_comments", 0),
            "post_date": datetime.fromtimestamp(raw_post_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
            "text_content": raw_post_data.get("selftext", "")
        }
    
    def is_post_relevant(self, post_data, search_query):
        query_words = search_query.lower().split()
        title_text = post_data.get("title", "").lower()
        content_text = post_data.get("text_content", "").lower()
        combined_text = f"{title_text} {content_text}"
        
        relevant_count = 0
        for word in query_words:
            if word in combined_text:
                relevant_count += 1
        
        return relevant_count >= len(query_words) * 0.6
    
    def extract_comment_data(self, raw_comment_data):
        return {
            "comment_author": raw_comment_data.get("author", "unknown"),
            "comment_text": raw_comment_data.get("body", ""),
            "comment_score": raw_comment_data.get("score", 0),
            "comment_date": datetime.fromtimestamp(raw_comment_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S")
        }
    

    
    def search(self, search_query, sort_by='hot', time_range='all'):
        try:
            if not search_query:
                return self.create_empty_result("No search query provided")
            
            print(f"Processing search for: {search_query}")
            reddit_response = self.fetch_reddit_data(search_query, sort_by, time_range, 25)
            
            if not reddit_response or "data" not in reddit_response:
                print("No reddit response or no data key")
                return self.create_empty_result(search_query)
            
            processed_posts = []
            
            for post_item in reddit_response["data"]["children"]:
                if post_item["kind"] != "t3":
                    continue
                    
                post_data = post_item.get("data", {})
                processed_post = self.extract_post_data(post_data)
                
                post_comments = []
                comments_response = self.fetch_post_comments(
                    processed_post["subreddit"], 
                    post_data.get("id", "")
                )
                
                if comments_response and len(comments_response) > 1:
                    for comment_item in comments_response[1]["data"]["children"]:
                        if (comment_item["kind"] == "t1" and 
                            comment_item.get("data", {}).get("body") not in ["[deleted]", "[removed]", ""]):
                            
                            comment_data = self.extract_comment_data(comment_item["data"])
                            post_comments.append(comment_data)
                
                post_comments.sort(key=lambda x: x["comment_score"], reverse=True)
                processed_post["top_comments"] = post_comments[:5]
                processed_posts.append(processed_post)
            
            return self.create_final_result(search_query, processed_posts)
        
        except Exception as e:
            print(f"Error during search: {e}")
            return self.create_empty_result(search_query)
    
    def create_empty_result(self, query):
        return {
            "search_query": query,
            "search_timestamp": datetime.now().isoformat(),
            "posts": [],
            "statistics": {
                "total_posts": 0,
                "total_upvotes": 0,
                "total_comments": 0,
                "average_score": 0
            }
        }
    
    def create_final_result(self, query, posts_list):
        total_posts = len(posts_list)
        total_upvotes = sum(post["upvotes"] for post in posts_list)
        total_comments = sum(post["comment_count"] for post in posts_list)
        avg_score = sum(post["score"] for post in posts_list) / total_posts if total_posts > 0 else 0
        
        return {
            "search_query": query,
            "search_timestamp": datetime.now().isoformat(),
            "posts": posts_list,
            "statistics": {
                "total_posts": total_posts,
                "total_upvotes": total_upvotes,
                "total_comments": total_comments,
                "average_score": round(avg_score, 2)
            }
        }
    
    def save_data_as_json(self, data_object, file_name):
        file_path = os.path.join(self.data_dir, f"{file_name}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_object, json_file, indent=2, ensure_ascii=False)
            return file_path
        except IOError:
            return None
    
    def load_data_from_json(self, file_name):
        if not file_name.endswith('.json'):
            file_name += '.json'
            
        file_path = os.path.join(self.data_dir, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        except (IOError, json.JSONDecodeError):
            return None
    
    def convert_data_to_csv(self, json_data):
        if not json_data or not json_data.get("posts"):
            return None
        
        csv_buffer = StringIO()
        csv_columns = [
            'title', 'author', 'subreddit', 'score', 'upvotes', 
            'comment_count', 'post_date', 'external_url', 'reddit_permalink'
        ]
        
        csv_writer = csv.DictWriter(csv_buffer, fieldnames=csv_columns)
        csv_writer.writeheader()
        
        for post in json_data["posts"]:
            csv_row = {}
            for column in csv_columns:
                csv_row[column] = post.get(column, '')
            csv_writer.writerow(csv_row)
        
        return csv_buffer.getvalue()
    
    def get_saved_files_list(self):
        saved_files = []
        
        if os.path.exists(self.data_dir):
            for file_name in os.listdir(self.data_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.data_dir, file_name)
                    file_stats = os.stat(file_path)
                    
                    saved_files.append({
                        "file_name": file_name,
                        "last_modified": datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "file_size_kb": round(file_stats.st_size / 1024, 2)
                    })
        
        saved_files.sort(key=lambda x: x["last_modified"], reverse=True)
        return saved_files
    
    def generate_safe_filename(self, query_text):
        safe_chars = "".join(char for char in query_text if char.isalnum() or char in (' ', '-', '_'))
        safe_name = safe_chars.replace(' ', '_').lower()[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_name}_{timestamp}"
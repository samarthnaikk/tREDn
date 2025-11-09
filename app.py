from flask import Flask, render_template, request, jsonify, Response
from utils import RedditUtils

app = Flask(__name__)
reddit_utils = RedditUtils()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    num_posts = int(request.form.get('num_posts', 10))
    sort = request.form.get('sort', 'top')
    time_filter = request.form.get('time_filter', 'month')
    
    try:
        results = reddit_utils.process_search_results(query, num_posts, sort, time_filter)
        
        filename = reddit_utils.generate_safe_filename(query)
        reddit_utils.save_data_as_json(results, filename)
        results["saved_filename"] = f"{filename}.json"
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files')
def list_files():
    return jsonify(reddit_utils.get_saved_files_list())

@app.route('/load/<filename>')
def load_file(filename):
    data = reddit_utils.load_data_from_json(filename)
    if data:
        return jsonify(data)
    return jsonify({"error": "File not found"}), 404

@app.route('/export/<filename>')
def export_csv(filename):
    data = reddit_utils.load_data_from_json(filename)
    if not data:
        return jsonify({"error": "File not found"}), 404
    
    csv_content = reddit_utils.convert_data_to_csv(data)
    if not csv_content:
        return jsonify({"error": "No data to export"}), 400
    
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename.replace('.json', '.csv')}"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
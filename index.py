from flask import Flask, request, send_file, redirect, url_for, render_template
import os
import pandas as pd
import get_data

app = Flask(__name__)

#what we if you visit the root URL
@app.route('/', methods=['GET'])
def form():
	return render_template('index.html')


@app.route('/get', methods=['POST'])
def get_weather():
	place = request.form.get('place', '').strip()
	if not place:
		place = 'New Delhi'

	lat, lon, display = get_data.get_place_from_user_and_geocode_for_web(place)
	result = get_data.fetch_and_process(latitude=lat, longitude=lon, place_name=display)

	# prepare values for template
	plot_name = os.path.basename(result['plot_image'])
	csv_name = os.path.basename(result['selected_csv'])
	raw_name = os.path.basename(result['raw_json'])

	# preview first 10 rows of CSV
	preview_rows = []
	try:
		df = pd.read_csv(result['selected_csv'])
		preview_rows = df.head(10).to_dict(orient='records')
	except Exception:
		preview_rows = []

	template_data = {
		'result': {
			'place': result['place'],
			'latitude': result['latitude'],
			'longitude': result['longitude'],
			'plot_image_name': plot_name,
			'selected_csv_name': csv_name,
			'raw_json_name': raw_name,
		},
		'preview_rows': preview_rows,
		'place': place,
		'error': None,
	}

	return render_template('index.html', **template_data)


@app.route('/plots/<path:filename>')
def serve_plot(filename):
	return send_file(os.path.join('plots', filename))


@app.route('/download_csv/<path:filename>')
def download_csv(filename):
	return send_file(os.path.join('plots', filename), as_attachment=True)


if __name__ == '__main__':
	os.makedirs('plots', exist_ok=True)
	app.run(host='0.0.0.0', port=5000, debug=True)
var Pipeline = React.createClass({

	getInitialState: function() {
		return {
			'nodes': []
		}
	},

	componentDidMount: function() {
		this.loadState();
	},

	render: function() {
		if (this.state.nodes.length) {
			return (
				<div className="pipeline">
					<NodesContainer nodes={this.state.nodes} />
				</div>
				)
		} else {
			return (
				<div className="loader"><span className="fa fa-circle-o-notch fa-spin"></span></div>
			)
		}
	},

	getNodeData: function(node) {
		var nodeData = {
			'name': node[0],
			'histogram': node[1]['histogram'],
			'avgTime': Utils.getISODuration(node[1]['avg_time_taken']),
			'percentile': Utils.getISODuration(node[1]['95_percentile']),
			'waiting': node[1]['waiting']
		};
		var nodeTitle = nodeData.name.replace(/([A-Z])/g, ' $1');
		nodeTitle = nodeTitle.split('-')[0].split(' ');
		var nodeType = nodeTitle.splice(nodeTitle.length-1, 1).join(' ').toLowerCase();
		nodeTitle = nodeTitle.join(' ');
		nodeData.title = nodeTitle;
		nodeData.nodeType = nodeType;

		var icons = {
			'ramp': 'truck',
			'intersection': 'exchange',
			'tap': 'truck',
			'transformer': 'exchange'
		};
		nodeData.iconClass = 'fa fa-'+icons[nodeType];

		nodeData.secondsRemaining = Utils.getSecondsFromDuration(nodeData.avgTime) * nodeData.waiting;

		nodeData.url = PipelineSettings.detailUrlPrefix + nodeData.name;

		return nodeData;
	},

	loadState: function() {
		var that = this;
		$.getJSON(PipelineSettings.apiUrl, function(data) {
			var nodes = [];
			var maxHistogramValue = 0;
			var lastMinutes = data['last_minutes'];
			$.each(data['sorted_process_statistics'], function(i, node) {
				var histogram = node[1]['histogram'];
				$.each(data['last_minutes'], function(i, minute) {
					var count = histogram[minute]['success_count'] + histogram[minute]['error_count'];
					if (maxHistogramValue < count) {
						maxHistogramValue = count;
					}
				});
				nodes.push(that.getNodeData(node));
			});
			$.each(nodes, function(i, node) {
				var histogram = node.histogram;
				$.each(node.histogram, function(i, item) {
					if (maxHistogramValue > 0) {
						histogram[i]['success_percentage'] = (item['success_count'] / maxHistogramValue) * 100;
						histogram[i]['error_percentage'] = (item['error_count'] / maxHistogramValue) * 100;
						histogram[i]['timeout_percentage'] = (item['timeout_count'] / maxHistogramValue) * 100;
					} else {
						histogram[i]['success_percentage'] = 0;
						histogram[i]['error_percentage'] = 0;
						histogram[i]['timeout_percentage'] = 0;
					}
				});
				node.histogram = histogram;
				node.latestHistogram = lastMinutes.map(function(minute) {
					return {
						'minute': minute,
						'value': node.histogram[minute]
					};
				});
			});
			if (that.isMounted()) {
				that.setState({
					'nodes': nodes,
					'maxHistogramValue': maxHistogramValue,
					'lastMinutes': lastMinutes
				});
			}
		})
		.done(function() {
			$('body').removeClass('disconnected');
		})
		.fail(function() {
			$('body').addClass('disconnected');
		})
		.always(function() {
			var pulse = $('#pulse');
			pulse.show();
			setTimeout(function() {
				pulse.hide();
			}, 100);
			setTimeout(function() {
				that.loadState();
			}, 1000);
		});
	}
});

React.render(<Pipeline />, document.querySelector('#container'));


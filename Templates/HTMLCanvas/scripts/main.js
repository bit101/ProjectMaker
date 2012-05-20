window.onload = function() {
	var canvas = document.getElementById("canvas"),
		context = canvas.getContext("2d"),
		width = window.innerWidth,
		height = window.innerHeight;

	init();

	function init() {
		canvas.width = width;
		canvas.height = height;
		context.fillStyle = "#ffcccc";
		context.fillRect(0, 0, width, height);
		context.fillStyle = "#000000";
		context.fillText("hello from ${project_name}", 100, 100);
	}

}
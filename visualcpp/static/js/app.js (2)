function App(app_data){
	this.FRAME_CONTAINER = "#frame-container";
	this.GLOBAL_VARIABLE_CONTAINER = "#global-variable-container";
	this.OBJECTS_CONTAINER = "#objects-container";

	this.FRAME_CONTAINER_TEMPLATE = "#frame-container-template";
	this.GLOBAL_VARIABLE_CONTAINER_TEMPLATE = "#global-variable-container-template";
	this.FRAME_TEMPLATE = "#frame-template";
	this.VARIABLE_TEMPLATE = "#variable-template";

	this.ARRAY_OBJECT_TEMPLATE = "#array-object-template";
	this.STRING_OBJECT_TEMPLATE = "#string-object-template";

	this.GLOBALS_AND_FRAME_SECTION_TEMPLATE = "#globals-and-frame-section-template";
	this.OBJECTS_SECTION_TEMPLATE = "#objects-section-template";

	this.VISUALIZATION_PANEL = "#visualization-panel";
	this.GLOBALS_AND_FRAME_SECTION = "#globals-and-frame-section";
	this.OBJECTS = "#objects-section";

	this.STEP_FORWARD_BUTTON = "#step-forward-button";
	this.STEP_BACKWARD_BUTTON = "#step-backward-button";
	this.CURRENT_STEP_INDICATOR = "#current-step";

	this.current_state = 0;
	this.data = app_data;
	this.no_of_steps = app_data.length;

	this.initialize_panel = function(){
		$(this.VISUALIZATION_PANEL).html("")
		$(this.VISUALIZATION_PANEL).append( $(this.GLOBALS_AND_FRAME_SECTION_TEMPLATE).html() );
		$(this.VISUALIZATION_PANEL).append( $(this.OBJECTS_SECTION_TEMPLATE).html() );
	};

	this.generate_object_html = function(obj){
		if(obj.type == "array"){
			var template = Handlebars.compile($(this.ARRAY_OBJECT_TEMPLATE).html());
			return template(obj);
		}
		else if(obj.type == "string"){
			var template = Handlebars.compile($(this.STRING_OBJECT_TEMPLATE).html());
			return template(obj);
		}
	}

	this.generate_frame_html = function(frame){
		var template = Handlebars.compile( $(this.FRAME_TEMPLATE).html() );
		return template( frame );
	};

	this.generate_variable_html = function(variable){
		var template = Handlebars.compile( $(this.VARIABLE_TEMPLATE).html() );
		return template( variable );
	};

	this.add_all_global_variables = function(){
		var all_globals = this.data[this.current_state].globals;
		var global_variable_container= $(this.GLOBAL_VARIABLE_CONTAINER);
		var i = 0;
		for(; i < all_globals.length; i++){
			global_variable_container.append(this.generate_variable_html(all_globals[i]) );
		}

		//If no global variable exists
		if(i == 0){
			global_variable_container.hide();
		}
	};

	this.add_all_frames = function(){
		var all_frames = this.data[this.current_state].frames
		var frame_container= $(this.FRAME_CONTAINER);

		for(var i = 0; i < all_frames.length; i++){
			var frame_html = $(this.generate_frame_html(all_frames[i]) );

			if(i == 0){
				frame_html.addClass("newest-frame");
			}


			//Get all the variables in each frame
			var frame_variables = all_frames[i].variables;
			for(var i = 0; i < frame_variables.length; i++){
				var frame_variable_html = this.generate_variable_html(frame_variables[i])
				frame_html.append(frame_variable_html)
			}
			frame_container.append(frame_html);
		}	
	};

	this.add_all_objects = function(){
		var all_objects = this.data[this.current_state].objects;
		var objects_container = $(this.OBJECTS_CONTAINER);

		var i = 0;
		for(; i < all_objects.length; i++){
			objects_container.append($(this.generate_object_html(all_objects[i])));
		}

	};

	this.change_step_indicator = function(){
		$(this.CURRENT_STEP_INDICATOR).html(this.current_state+1);
	};

	this.change_state = function(state_num){
		if(state_num <= this.no_of_steps-1 && state_num >= 0){
			this.current_state = state_num;
			this.start(); //restart
			this.change_step_indicator();
		}
	};

	this.step_forward = function(){
		this.change_state(this.current_state+1);
	};

	this.step_backward = function(){
		this.change_state(this.current_state-1);
	};

	this.start = function(){
		this.initialize_panel();
		this.add_all_frames();
		this.add_all_global_variables();
		this.add_all_objects();
		$(this.VISUALIZATION_PANEL).show();
	}

};


if($("#visualization-result").length > 0){ 
	var result_json = $("#visualization-result").html();
	var app_data = eval(result_json);
	var newApp = new App(app_data);
	newApp.start();

	$(newApp.STEP_FORWARD_BUTTON).click(function(e){
		e.stopPropagation();
		e.preventDefault();
		newApp.step_forward()
	});

	$(newApp.STEP_BACKWARD_BUTTON).click(function(e){
		e.stopPropagation();
		e.preventDefault();
		newApp.step_backward()
	});
}



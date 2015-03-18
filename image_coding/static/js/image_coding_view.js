/* Javascript for cs101XBlock. */
function ImageCodingXBlockInitView(runtime, element) {
    
    var handlerUrl = runtime.handlerUrl(element, 'student_submit');
    var hintUrl = runtime.handlerUrl(element, 'send_hints');
	var publishUrl = runtime.handlerUrl(element, 'publish_event');

	var $element = $(element);
	
    var submit_button = $element.find('.submit_button');
    var hint_button = $element.find('hint_button');
    var reset_button = $element.find('.reset_button');

    var unanswered = $element.find('.unanswered');
    var correct = $element.find('.correct');
    var incorrect = $element.find('.incorrect');

    var correct_feedback = $element.find('.correct_feedback');

    var hint_div = $element.find('.hint');

	var hint_counter = 0;
    var student_code = "";
    
	var ta = document.getElementById('jsinputid');
	var initial_code = ta.value;

    var hint;
    var hints;
    var hint_counter = 0;
	
    $.ajax({
        type: 'POST',
        url: hintUrl,
        data: JSON.stringify({requested: true}),
        success: set_hints
    });

    function publish_event(data) {
      $.ajax({
          type: "POST",
          url: publishUrl,
          data: JSON.stringify(data)
      });
    }

	function post_submit(result) {
	}
	
	function set_hints(result) {
		hints = result.hints;
		if (hints.length > 0) {
	        hint_button.css('display','inline');
			hint_button_holder.css('display','inline');
    	}
	}

	function show_unanswered() {
		console.log('show_unanswered');
		unanswered.css('display','block');
		correct.css('display','none');
		incorrect.css('display','none');
		correct_feedback.css('display','none');
	}

	function show_correct() {
		console.log('show_correct');
		unanswered.css('display','none');
		correct.css('display','block');
		incorrect.css('display','none');
		correct_feedback.css('display','block');
	}

	function show_incorrect() {
		console.log('show_incorrect');
		unanswered.css('display','none');
		correct.css('display','none');
		incorrect.css('display','block');
		correct_feedback.css('display','none');
	}

    function reset_answer() {
		hint_div.css('display','none');
		show_unanswered();
		try {
			clearOutput();
		}
		catch (e) {
		}
		var ta = document.getElementById('jsinputid');
		ta.value = initial_code;
    }

    function reset_hint() {
    	hint_counter = 0;
    	hint_div.css('display','none');
    }

    function show_hint() {
    	hint = hints[hint_counter];
		hint_div.html(hint);
		hint_div.css('display','block');
		publish_event({
			event_type:'hint_button',
			next_hint_index: hint_counter,
		});
		if (hint_counter == (hints.length - 1)) {
			hint_counter = 0;
		} else {
			hint_counter++;
		}
    }

    $('.submit_button', element).click(function(eventObject) {
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify({'answer': $('.answer',element).val() }),
            success: post_submit
        });
  		try {
  			var grade = evaluateGrade('jsinputid');
  		}
  		catch (e) {
  		}
  		console.log(grade);
        if (grade) {
        	show_correct();
        } else {
        	show_incorrect();
        }
	});

    $('.run_button', element).click(function(eventObject) {
  		evaluateClear("jsinputid");
		var ta = document.getElementById('jsinputid');
		var text = ta.value;
  		console.log(text);

		publish_event({
			event_type:'run_button',
			student_code: text,
		});
	});

    $('.hint_button', element).click(function(eventObject) {
        show_hint();
	});

    $('.reset_button', element).click(function(eventObject) {
        reset_answer();
	});
	
 
}



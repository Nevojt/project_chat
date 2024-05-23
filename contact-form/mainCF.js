document.addEventListener('DOMContentLoaded', function() {
	document.getElementById("contactForm").addEventListener('submit', function(event) {
		event.preventDefault();

		var form = event.target;
		var name = form.querySelector('#name').value.trim();
		var email = form.querySelector('#email').value.trim();
		var subject = form.querySelector('#subject').value.trim();
		var message = form.querySelector('#message').value.trim();
		var warning = form.querySelector('#formMassageWarning');

		var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		var isValid = true;
		var errorMessage = '';

		if (!name) {
			isValid = false;
			errorMessage += 'Name is required.<br>';
		}

		if (!email) {
			isValid = false;
			errorMessage += 'Email is required.<br>';
		} else if (!emailPattern.test(email)) {
			isValid = false;
			errorMessage += 'Invalid email format.<br>';
		}

		if (!message) {
			isValid = false;
			errorMessage += 'Message is required.<br>';
		}

		if (isValid) {
			if (warning) {
				warning.innerHTML = '';
			}
			alert('Form is valid and ready to be submitted');
		} else {
			if (warning) {
				warning.innerHTML = errorMessage;
				warning.style.display = 'block'; // Ensure the warning is displayed
			} else {
				console.error('Element with id "form-message-warning" not found.');
			}
		}
	});
});




























// (function($) {

// 	"use strict";

// 	// Form
// 	var contactForm = function() {
// 			if ($('#contactForm').length > 0) {
// 					$("#contactForm").validate({
// 							rules: {
// 									name: "required",
// 									subject: "required",
// 									email: {
// 											required: true,
// 											email: true
// 									},
// 									message: {
// 											required: true,
// 											minlength: 5
// 									}
// 							},
// 							messages: {
// 									name: "Please enter your name",
// 									subject: "Please enter your subject",
// 									email: "Please enter a valid email address",
// 									message: "Please enter a message"
// 							},
// 							/* submit via ajax */
// 							submitHandler: function(form) {
// 									var $submit = $('.submitting'),
// 											waitText = 'Submitting...';

// 									// Збір даних з форми у JSON-формат
// 									var formData = {
// 											name: $(form).find('input[name="name"]').val(),
// 											email: $(form).find('input[name="email"]').val(),
// 											subject: $(form).find('input[name="subject"]').val(),
// 											message: $(form).find('textarea[name="message"]').val()
// 									};

// 									$.ajax({
// 											type: "POST",
// 											url: "php/sendEmail.php",
// 											data: JSON.stringify(formData), // Перетворення об'єкта у JSON-строку
// 											contentType: "application/json; charset=utf-8", // Встановлення MIME-типу JSON
// 											beforeSend: function() {
// 													$submit.css('display', 'block').text(waitText);
// 											},
// 											success: function(msg) {
// 													if (msg === 'OK') {
// 															$('#form-message-warning').hide();
// 															setTimeout(function() {
// 																	$('#contactForm').fadeIn();
// 															}, 1000);
// 															setTimeout(function() {
// 																	$('#form-message-success').fadeIn();
// 															}, 1400);
// 															setTimeout(function() {
// 																	$('#form-message-success').fadeOut();
// 															}, 8000);
// 															setTimeout(function() {
// 																	$submit.css('display', 'none').text(waitText);
// 															}, 1400);
// 															setTimeout(function() {
// 																	$('#contactForm')[0].reset();
// 															}, 1400);
// 													} else {
// 															$('#form-message-warning').html(msg).fadeIn();
// 															$submit.css('display', 'none');
// 													}
// 											},
// 											error: function() {
// 													$('#form-message-warning').html("Something went wrong. Please try again.").fadeIn();
// 													$submit.css('display', 'none');
// 											}
// 									});
// 							} // end submitHandler
// 					});
// 			}
// 	};
// 	contactForm();

// })(jQuery);
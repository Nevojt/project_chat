document.addEventListener('DOMContentLoaded', function() {
  var contactForm = document.getElementById("contactForm");
  var warning = document.getElementById("form-message-warning");
  
  if (contactForm) {
      contactForm.addEventListener('submit', function(event) {
          event.preventDefault();

          var form = event.target;
          var name = form.querySelector('#name').value.trim();
          var email = form.querySelector('#email').value.trim();
          var subject = form.querySelector('#subject').value.trim();
          var message = form.querySelector('#message').value.trim();

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

          if (!subject) {
              isValid = false;
              errorMessage += 'Subject is required.<br>';
          }

          if (!message) {
              isValid = false;
              errorMessage += 'Message is required.<br>';
          }

          if (isValid) {
              if (warning) {
                  warning.innerHTML = '';
                  warning.style.display = 'none';
              }
              alert('Form is valid and ready to be submitted');
              // Тут можна додати код для відправки форми
          } else {
              if (warning) {
                  warning.innerHTML = errorMessage;
                  warning.style.display = 'block';
              } else {
                  console.error('Element with id "form-message-warning" not found.');
              }
          }
      });
  } else {
      console.error('Element with id "contactForm" not found.');
  }
});

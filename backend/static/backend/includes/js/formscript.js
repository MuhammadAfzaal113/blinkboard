
  $(document).ready(function () {
    $(".bb--screen-block.signup--screen , .form__alert").hide();
    // Switch to signup form on click
    $(".bb-form__switcher").on("click", function (e) {
      e.preventDefault();
      $(".bb--screen-block.login--screen").toggle();
      $(".bb--screen-block.signup--screen").toggle();
    });
    // Show alert on signup button click
    $(".bb-form__btn").on("click", function (e) {
      e.preventDefault();
      $(".form__alert").hide();
      $(this).siblings(".form__alert").show();
    });
    
  });


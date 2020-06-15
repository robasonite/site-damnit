(function site_js() {

  // A couple of useful function in a conveniant IIFE

  // Sleep function for use with 'async' functions
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }


  /* Automatically append "target='_blank'" to all outbound links */
  function js_target_links() {
    var links = document.links;

    for (var i = 0, linksLength = links.length; i < linksLength; i++) {
      if (links[i].hostname != window.location.hostname) {
        links[i].target = '_blank';
      } 
    }
  }

  // Run functions as soon at this executes
  js_target_links()
}());

// Make the menu button work
document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  let mobileBurger = document.getElementById("mobile-menu-button");
  let mobileMenu = document.getElementById("responsiveNav");

  mobileBurger.addEventListener('click', () => {

    mobileBurger.classList.toggle('is-active');
    mobileMenu.classList.toggle('is-active');

  });
});

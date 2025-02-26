document.addEventListener('DOMContentLoaded', () => {
  // Get the navbar-burger element
  const navbarBurger = document.getElementById('navbar-burger')
  
  if (navbarBurger) {
    navbarBurger.addEventListener('click', () => {
      // Get the target from the "data-target" attribute
      const target = navbarBurger.dataset.target
      const $target = document.getElementById(target)

      // Toggle menu visibility
      if ($target) {
        const isVisible = $target.style.display !== 'none'
        $target.style.display = isVisible ? 'none' : 'block'
      }
    })
  }
})

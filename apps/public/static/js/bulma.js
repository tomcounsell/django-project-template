document.addEventListener('DOMContentLoaded', () => {
  ;(document.querySelectorAll('.notification .delete') || []).forEach(
    ($delete) => {
      const $notification = $delete.parentNode

      $delete.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification)
      })
    }
  )
})

// modal handlers

document.addEventListener('DOMContentLoaded', () => {
  // Functions to open and close a modal
  function openModal($el) {
    $el.classList.add('is-active')
  }

  function closeModal($el) {
    $el.classList.remove('is-active')
  }

  function closeAllModals() {
    ;(document.querySelectorAll('.modal') || []).forEach(($modal) => {
      closeModal($modal)
    })
  }

  // Add a click event on buttons to open a specific modal
  ;(document.querySelectorAll('.modal-trigger') || []).forEach(($trigger) => {
    const modal = $trigger.dataset.target
    const $target = document.getElementById(modal)

    $trigger.addEventListener('click', () => {
      openModal($target)
    })
  })
})

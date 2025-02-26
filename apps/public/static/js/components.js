// Generic component functionality

document.addEventListener('DOMContentLoaded', () => {
  // Notification close functionality
  (document.querySelectorAll('.close-button') || []).forEach(
    ($closeButton) => {
      const $notification = $closeButton.parentNode

      $closeButton.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification)
      })
    }
  )
  
  // Simple modal functionality will be implemented later
})

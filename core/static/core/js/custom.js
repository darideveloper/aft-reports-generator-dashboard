class AdminSetup {

  /**
   * Setup global data
   */
  constructor() {

    // Get current page
    this.currentPage = document.querySelector('h1').textContent.toLowerCase().trim()
    console.log(this.currentPage)

    // Run methods in each page
    this.autorun()
  }

  /**
 * Load the base image (image, logo, icon, etc) who match with the selector
 * 
 * @param {string} selector - The css selector to find the images
 * @param {string} className - The class name to add to the image
 */
  #renderBaseImage(imageWrapper, className) {
    // Get link
    const link = imageWrapper.href

    // Create image tag
    const imageElem = document.createElement("img")
    imageElem.classList.add(className)
    imageElem.classList.add("rendered-media")
    imageElem.src = link

    // Append element to the wrapper
    imageWrapper.innerHTML = ""
    imageWrapper.appendChild(imageElem)
    imageWrapper.target = "_blank"
  }

  /**
   * Render regular image images
   * 
   * @param {string} selector_images - The css selector to find the images
   */
  renderImages(selector_images) {
    const images = document.querySelectorAll(selector_images)
    images.forEach(imageWrapper => {
      this.#renderBaseImage(imageWrapper, "rendered-image")
    })
  }

  /**
   * Run the functions for the current page
   */
  autorun() {
    // Methods to run for each page
    const methods = {
      "imágenes de galería": [() => this.renderImages('.field-image a'), this.setupCopyButtons],
    }

    // Run the methods for the current page
    if (methods[this.currentPage]) {
      for (let method of methods[this.currentPage]) {
        method.call(this)
      }
    }
  }
}

new AdminSetup()
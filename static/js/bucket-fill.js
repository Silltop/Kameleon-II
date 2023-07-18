   function fillContainerById(amount, containerId) {
    const container = document.getElementById(containerId);
    const parent = container.parentNode;

    // Calculate the fill height
    const fillHeight = (amount / 100) * parent.offsetHeight;

    // Apply the fill height to the container
    container.style.height = `${fillHeight}px`;

    // Change the background color based on the fill amount
    if (amount >= 90) {
      container.style.backgroundColor = '#3f0d12';
      container.style.backgroundImage = 'linear-gradient(315deg, #ff7878 0%, #ff0000 74%)';
    } else if (amount >= 75) {
      container.style.backgroundColor = '#f5d020';
      container.style.backgroundImage = 'linear-gradient(315deg, #f5d020 0%, #f53803 74%)';
    } else {
      container.style.backgroundColor = '#00b712';
      container.style.backgroundImage = 'linear-gradient(315deg, #1A512E, #00b712, #5aff15, #182C25)';
    }
  }
<form id="multiUploadForm">
  <div id="itemsContainer">
    <div class="item">
      <input type="text" name="item" placeholder="Item name" required>
      <input type="text" name="food" placeholder="Food description" required>
      <input type="number" name="price" placeholder="Price" required>
      <input type="file" name="picture" accept="image/*" required>
    </div>
  </div>
  
  <button type="button" id="addMore">+ Add Another Item</button>
  <button type="submit">Submit</button>
</form>

<script>
document.getElementById("addMore").addEventListener("click", () => {
  const container = document.getElementById("itemsContainer");
  const newItem = document.createElement("div");
  newItem.classList.add("item");
  newItem.innerHTML = `
    <input type="text" name="item" placeholder="Item name" required>
    <input type="text" name="food" placeholder="Food description" required>
    <input type="number" name="price" placeholder="Price" required>
    <input type="file" name="picture" accept="image/*" required>
  `;
  container.appendChild(newItem);
});

document.getElementById("multiUploadForm").addEventListener("submit", async (e) => {
  e.preventDefault(); // Prevents form from reloading the page

  const items = [];
  const user_id = sessionStorage.getItem("user_id"); // would come from sessionStorage or server
  
  const itemDivs = document.querySelectorAll("#itemsContainer .item");

  for (let div of itemDivs) {
    const itemName = div.querySelector('input[name="item"]').value;
    const foodDesc = div.querySelector('input[name="food"]').value;
    const price = parseFloat(div.querySelector('input[name="price"]').value);
    const fileInput = div.querySelector('input[name="picture"]');
    const file = fileInput.files[0];

    // Convert file to base64
    const base64Data = await toBase64(file);

    items.push({
      item: itemName,
      food: foodDesc,
      price: price,
      picture_filename: file.name,
      picture_type: file.type,
      picture_data: base64Data
    });
  }

  const payload = { user_id, items };

  const response = await fetch("/items", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  console.log(result);
});

function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(",")[1]); // remove `data:image/...;base64,`
    reader.onerror = error => reject(error);
  });
}
</script>


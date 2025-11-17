# TODO List for e-Devlet Improvements

## 1. Add Verification Animation on Index Page
- [ ] Modify `templates/index.html` to include a verification modal/overlay
- [ ] Add JavaScript to handle form submit: prevent default, show animation for 10 seconds
- [ ] Implement animation phases: "Kartınız doğrulanıyor..." (5s), "Bankanız doğrulanıyor..." with bank logo (5s)
- [ ] Enhance bin-lookup to fetch and display bank logo
- [ ] Add CSS styles for the verification modal in `static/css/giris.css`
- [ ] Test the animation flow and timing

## 2. Improve Congratulations Page
- [ ] Modify `templates/tebrikler.html` to make sections smaller
- [ ] Add animations to the congratulations elements (fade-in, scale, etc.)
- [ ] Update CSS in `static/css/giris.css` for better styling and animations

## 3. Develop Admin Panel
- [ ] Review admin templates in `templates/admin/`
- [ ] Add animations and improve UI elements
- [ ] Enhance responsiveness and user experience

## 4. Bank Logo Integration
- [ ] Create a mapping for bank names to logo URLs in `app/binlookup.py`
- [ ] Add bank logo images to `static/img/banks/` if needed
- [ ] Ensure logos display correctly in verification animation

## 5. Testing and Validation
- [ ] Test the entire flow from index to congratulations
- [ ] Validate animations work on different devices/browsers
- [ ] Ensure bin-lookup and bank info display correctly

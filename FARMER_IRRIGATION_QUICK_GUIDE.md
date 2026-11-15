# FieldShift FarmOS - Water Supply Quick Guide for Farmers

## How to Tell the System About Your Water Supply

The "What If Conditions Change?" section now lets you enter your water supply in everyday terms - no need to know technical measurements!

---

## Step 1: Enter Your Field Size

**Choose the unit that makes sense to you:**

### Option A: Square Meters (m²)
- Small plot: 100-500 m²
- Medium plot: 500-2,000 m²
- Large plot: 2,000-10,000 m²

### Option B: Hectares (ha)
- 1 hectare = 10,000 m² = 2.5 acres
- Small farm: 0.1-0.5 hectares
- Medium farm: 0.5-2 hectares
- Large farm: 2-10 hectares

**Example:** If you have a plot that's 50m × 20m, that's 1,000 m² (or 0.1 hectares)

---

## Step 2: Select How You Water Your Crops

### 🌧️ Rainwater Only
**Choose this if:**
- You don't add any water yourself
- You only depend on rain
- You have no irrigation system

**What happens:**
- System will plan rotations based only on rainfall
- No irrigation capacity is added to calculations

---

### 🪣 Bucket or Watering Can
**Choose this if:**
- You water by hand with buckets or watering cans
- You fetch water from a well, tank, or tap

**You'll need to know:**

1. **Bucket/Can Size** (in litres)
   - Look at your bucket - usually marked on the side
   - Common sizes: 10L, 15L, 20L
   - If not marked, fill a 1L bottle and count how many fit

2. **How Many Buckets Per Day?**
   - On a typical watering day, count your buckets
   - Don't worry about exact numbers - estimate is fine
   - Example: "I use about 5 buckets each time I water"

3. **How Many Days Per Week Do You Water?**
   - 2-3 days = light watering
   - 4-5 days = regular watering  
   - 6-7 days = frequent watering

**Example:**
```
Bucket size: 10 litres
Buckets per day: 5
Days per week: 3

System calculates: 10 × 5 × 3 = 150 litres per week
```

---

### ⚙️ Pump or Irrigation System
**Choose this if:**
- You have a motorized water pump
- You have drip irrigation, sprinklers, or hoses
- You have a permanent irrigation setup

**You'll need to measure your pump flow rate.**

#### 📏 How to Measure Your Pump Flow Rate

**What you need:**
- A large bucket or container (10-20 litres is good)
- A stopwatch or your phone timer
- Your pump running

**Steps:**

1. **Get your container ready**
   - Place it under the pump outlet or hose end
   - Make sure it can catch all the water

2. **Start timing**
   - Turn on the pump
   - Start your timer at the same moment

3. **Fill for 1 minute**
   - Let the water run for exactly 60 seconds
   - Keep the pump at normal operating speed

4. **Stop and measure**
   - Turn off pump and timer together
   - Measure how many litres you collected

5. **That's your flow rate!**
   - If you collected 15 litres → Your flow rate is **15 litres/minute**
   - If you collected 30 litres → Your flow rate is **30 litres/minute**

**Tips:**
- Do this test 2-3 times and take the average
- Use the actual measured flow, not what's written on the pump
- If your hose has a valve, measure with it set to normal use

**Then enter:**

1. **Flow Rate** (litres/minute)
   - The number you just measured
   - Example: 20 L/min

2. **How Many Minutes Per Day?**
   - How long do you run the pump each watering day?
   - Example: 30 minutes

3. **How Many Days Per Week?**
   - How many days do you irrigate?
   - Example: 3 days

**Example:**
```
Flow rate: 20 litres/minute
Minutes per day: 30
Days per week: 3

System calculates: 20 × 30 × 3 = 1,800 litres per week
```

---

### ❓ Not Sure / Not Measured
**Choose this if:**
- You haven't measured your water supply yet
- You're still planning your irrigation
- You want to see what rotations need before committing

**What happens:**
- System shows "Water supply not yet measured"
- You can still explore other features
- Come back after measuring to get specific recommendations

---

### 🔬 Advanced (mm/week)
**Choose this only if:**
- You already know your irrigation capacity in mm/week
- You have scientific irrigation data
- An agronomist gave you this number

**Most farmers should use Bucket or Pump options instead!**

---

## Step 3: Adjust Irrigation Efficiency (Optional)

**This tells the system how much of your water actually reaches the plant roots.**

Not all water you apply reaches the plants because of:
- Some runs off the field
- Some evaporates
- Some drains too deep

**Default: 70%** - This works well for most situations

**When to adjust:**

### Lower Efficiency (50-60%)
- Watering on sloped land (runoff)
- Watering in hot midday sun (evaporation)
- Very sandy soil (rapid drainage)
- Surface flooding methods

### Higher Efficiency (80-90%)
- Drip irrigation systems
- Mulched fields (reduces evaporation)
- Watering in early morning/evening
- Well-designed systems

**Don't worry too much about this!** The 70% default is a good starting point.

---

## Understanding Your Results

After you enter your details, the system shows three numbers:

### 1. Weekly Water Volume (litres/week)
**This is the total water you apply**
- Example: 1,500 litres/week
- This is the amount you pump or carry

### 2. Effective Irrigation Depth (mm/week)
**This is the scientific measurement**
- Example: 10.5 mm/week
- This is what the crop models use
- You don't need to understand this - it's calculated for you!

### 3. Water Per m² (litres/m²/week)
**This is water per square meter**
- Example: 1.5 litres/m²/week
- Helps you compare to other farms

---

## Common Questions

### Q: What if I don't irrigate every week the same?
**A:** Enter your typical or average pattern. The system uses weekly averages.

### Q: What if it rains and I don't water that week?
**A:** The system accounts for rainfall separately using NASA data. Your irrigation is the water YOU add on top of rain.

### Q: My pump rating says 50 L/min but I measured 30 L/min. Which do I use?
**A:** Always use your MEASURED flow (30 L/min). Real flow is usually less than the pump rating because of hoses, height, and restrictions.

### Q: I have different sized buckets. What do I enter?
**A:** Use your most common bucket size, or calculate the total litres per day and enter that as one "bucket."

### Q: Can I change this later?
**A:** Yes! All inputs can be adjusted anytime. As you measure things more accurately, come back and update.

### Q: What if my field is an odd shape?
**A:** Measure the length and width of the main area and multiply (Length × Width = Area in m²). For very irregular shapes, estimate the average area.

---

## Examples: Real Farmer Scenarios

### Example 1: Small Vegetable Garden
```
Field: 200 m²
Method: Watering Can
Can size: 10 litres
Cans per day: 8
Days per week: 5
Efficiency: 60% (some spillage)

Result: 400 litres/week = 1.2 mm/week effective
```

### Example 2: Medium Farm with Hose
```
Field: 2,000 m² (0.2 hectares)
Method: Pump
Flow rate: 25 L/min (measured with bucket test)
Minutes per day: 45
Days per week: 3
Efficiency: 70% (surface irrigation)

Result: 3,375 litres/week = 1.2 mm/week effective
```

### Example 3: Large Farm with Drip System
```
Field: 1 hectare (10,000 m²)
Method: Pump
Flow rate: 100 L/min (measured at drip header)
Minutes per day: 120 (2 hours)
Days per week: 4
Efficiency: 90% (drip irrigation)

Result: 48,000 litres/week = 4.3 mm/week effective
```

### Example 4: Rainfed Only
```
Field: 0.5 hectares
Method: Rainwater Only

Result: 0 litres irrigation, depends entirely on rainfall
System will recommend drought-tolerant rotations
```

---

## What to Do If You Don't Know Something

**Don't have a stopwatch?** Use your phone timer.

**Don't know your bucket size?** Fill a 1-litre bottle and count how many fit.

**Not sure about efficiency?** Use the default 70% - it's fine!

**Haven't measured flow yet?** Choose "Not Sure / Not Measured" and come back later.

**Field size unknown?** Measure with a tape measure or count your steps (1 step ≈ 0.75m).

---

## Pro Tips

1. **Measure during normal operation** - Don't test your pump at maximum if you normally run it slower

2. **Account for reality** - If you sometimes forget to water or it's too hot to work, reduce your days/week accordingly

3. **Start conservative** - Better to underestimate your water supply and be pleasantly surprised than overestimate and have crop stress

4. **Update as you learn** - First time through, estimate. As you farm, come back with real measurements.

5. **Check after changes** - If you upgrade your pump, get a bigger container, or install drip irrigation, update your inputs!

---

## Still Confused?

**The system is flexible!** You can:
- Start with rough estimates
- Update later with better numbers
- Try different scenarios to see "what if"
- Always see the calculations explained

**Remember:** Even a rough estimate of your water supply is better than using a default value. The system will help you understand what your crops need and whether your water supply can meet it.

---

## Need Help?

If you're still not sure what to enter:
1. Choose "Not Sure / Not Measured" for now
2. Use the other features (Planting Suitability, NASA climate data)
3. Come back to this section after you've measured your water supply
4. Start with conservative estimates rather than guessing high

The goal is to help you make better decisions with the information you have, not to require perfect data!

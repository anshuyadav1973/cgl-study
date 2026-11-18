import json
import os

test_1 = {
    "id": "cgl-mains-mock-01",
    "title": "SSC CGL Mains 2026 - Maths Full Mock Test #01",
    "subtitle": "Latest 2025-26 PYQs Chapterwise Selection (Mixed Tier-2 Pattern)",
    "category": "Full Length Mock",
    "durationMinutes": 35,
    "marksPerQuestion": 3,
    "negativeMarks": 1,
    "instructions": [
        "This test consists of 25 questions based on the latest SSC CGL Mains 2025-26 pattern.",
        "Total time allotted is 35 minutes.",
        "Each correct answer awards +3 marks, and each incorrect answer deducts -1 mark.",
        "No marks are deducted for unattempted questions.",
        "Use the Question Palette on the right to navigate between questions.",
        "You can mark questions for review and toggle between English and Hindi anytime."
    ],
    "questions": [
        {
            "id": 1,
            "topic": "Percentage",
            "exam": "SSC CHSL Tier-II, 10/04/2026",
            "question_en": "A student scores 30% marks and fails by 12 marks, while another student scores 44% marks and gets 16 marks more than the pass marks. What is the maximum mark of the exam?",
            "question_hi": "एक छात्र 30% अंक प्राप्त करता है और 12 अंकों से फेल हो जाता है, जबकि दूसरा छात्र 44% अंक प्राप्त करता है और उत्तीर्ण अंक से 16 अंक अधिक पाता है। परीक्षा के अधिकतम अंक कितने हैं?",
            "options": [
                {"id": "A", "text": "200"},
                {"id": "B", "text": "240"},
                {"id": "C", "text": "280"},
                {"id": "D", "text": "320"}
            ],
            "correct": "A",
            "solution": "30% + 12 = 44% – 16\n⇒ (44% - 30%) = 12 + 16\n⇒ 14% = 28\n⇒ 1% = 2\n⇒ 100% (Maximum Marks) = 200.",
            "trick": "Difference in percentage = 44% - 30% = 14%. Difference in marks = 16 - (-12) = 28. 14% = 28 ⇒ 100% = 200."
        },
        {
            "id": 2,
            "topic": "Percentage",
            "exam": "SSC CGL Tier-II, 07/03/2023",
            "question_en": "If 20% of (A + B) = 30% of (A – B), then what percentage of B is equal to A?",
            "question_hi": "यदि (A + B) का 20% = (A – B) का 30%, तो B का कितना प्रतिशत A के बराबर है?",
            "options": [
                {"id": "A", "text": "400%"},
                {"id": "B", "text": "300%"},
                {"id": "C", "text": "500%"},
                {"id": "D", "text": "100%"}
            ],
            "correct": "C",
            "solution": "20/100 (A + B) = 30/100 (A – B)\n⇒ 2A + 2B = 3A – 3B\n⇒ A = 5B\n⇒ A/B = 5/1\nRequired % = (A/B) × 100% = (5/1) × 100% = 500%.",
            "trick": "By Componendo & Dividendo: (A + B)/(A - B) = 3/2 ⇒ A/B = (3+2)/(3-2) = 5/1 ⇒ 500%."
        },
        {
            "id": 3,
            "topic": "Ratio & Proportion",
            "exam": "SSC CGL Tier-II, 19/01/2026",
            "question_en": "₹4800 is divided among A, B, and C in the ratio 3:4:5. How much more is B’s share than A’s share?",
            "question_hi": "₹4800 की राशि को A, B और C के बीच 3:4:5 के अनुपात में विभाजित किया गया है। B का हिस्सा A के हिस्से से कितना अधिक है?",
            "options": [
                {"id": "A", "text": "₹200"},
                {"id": "B", "text": "₹400"},
                {"id": "C", "text": "₹300"},
                {"id": "D", "text": "₹500"}
            ],
            "correct": "B",
            "solution": "Total ratio units = 3 + 4 + 5 = 12 units.\n12 units = ₹4800 ⇒ 1 unit = ₹400.\nDifference between B and A = 4 - 3 = 1 unit = ₹400.",
            "trick": "(B - A) share = (4 - 3)/12 × 4800 = 1/12 × 4800 = ₹400."
        },
        {
            "id": 4,
            "topic": "Ratio & Proportion",
            "exam": "SSC CGL Tier-II, 20/01/2025",
            "question_en": "If a : b = 2 : 3 and b : c = 5 : 7, then find the ratio c : a.",
            "question_hi": "यदि a : b = 2 : 3, b : c = 5 : 7 है, तो c : a का अनुपात ज्ञात कीजिए।",
            "options": [
                {"id": "A", "text": "15 : 21"},
                {"id": "B", "text": "20 : 21"},
                {"id": "C", "text": "21 : 10"},
                {"id": "D", "text": "10 : 21"}
            ],
            "correct": "C",
            "solution": "a/b = 2/3 and b/c = 5/7\n⇒ a/c = (a/b) × (b/c) = (2/3) × (5/7) = 10/21\nTherefore, c : a = 21 : 10.",
            "trick": "c/a = (c/b) × (b/a) = (7/5) × (3/2) = 21/10."
        },
        {
            "id": 5,
            "topic": "Profit & Loss",
            "exam": "SSC CGL Tier-II, 20/01/2025",
            "question_en": "A man sells a mobile phone for ₹680 and loses something. If he had sold it for ₹1070, his gain would have been double the former loss. The cost price (in ₹) of the mobile phone is:",
            "question_hi": "एक आदमी ₹680 में एक मोबाइल फोन बेचता है और कुछ हानि उठाता है। यदि उसने इसे ₹1070 में बेचा होता, तो उसका लाभ, पूर्व की हानि का दोगुना होता। मोबाइल फोन का लागत मूल्य (₹ में) ज्ञात कीजिए।",
            "options": [
                {"id": "A", "text": "820"},
                {"id": "B", "text": "800"},
                {"id": "C", "text": "830"},
                {"id": "D", "text": "810"}
            ],
            "correct": "D",
            "solution": "Let cost price be CP.\nLoss at ₹680 = CP - 680.\nProfit at ₹1070 = 1070 - CP.\nGiven: 1070 - CP = 2(CP - 680)\n⇒ 1070 - CP = 2CP - 1360\n⇒ 3CP = 2430 ⇒ CP = ₹810.",
            "trick": "Difference in SP = 1070 - 680 = 390. This covers 1 unit loss + 2 units profit = 3 units. 1 unit = 390/3 = 130. CP = 680 + 130 = ₹810."
        },
        {
            "id": 6,
            "topic": "Profit & Loss",
            "exam": "SSC CGL Tier-II, 16/11/2020",
            "question_en": "A T.V. is sold at 8% gain. Had it been sold for ₹714 more, the gain would have been 15%. To gain 18%, the selling price of the T.V. should be:",
            "question_hi": "किसी टी.वी. को 8% लाभ पर बेचा जाता है। यदि इसे ₹714 अधिक में बेचा जाता, तो लाभ 15% होता। 18% लाभ प्राप्त करने के लिए, टी.वी. का विक्रय मूल्य कितना होना चाहिए?",
            "options": [
                {"id": "A", "text": "₹12138"},
                {"id": "B", "text": "₹12036"},
                {"id": "C", "text": "₹11934"},
                {"id": "D", "text": "₹12240"}
            ],
            "correct": "B",
            "solution": "Difference in profit% = 15% - 8% = 7%.\n7% of CP = ₹714 ⇒ 1% = ₹102.\nSelling price for 18% gain = 118% of CP = 118 × 102 = ₹12036.",
            "trick": "Unit digit check: 8 × 2 = 16 (last digit 6). Only ₹12036 ends with 6."
        },
        {
            "id": 7,
            "topic": "Discount",
            "exam": "SSC CGL Tier-II, 02/03/2023",
            "question_en": "A motor cycle is sold at a discount of 44% on its marked price for ₹87500. What is the marked price (in ₹) of the motor cycle?",
            "question_hi": "एक मोटर साइकिल को उसके अंकित मूल्य पर 44% की छूट देकर ₹87500 में बेचा जाता है। मोटर साइकिल का अंकित मूल्य (₹ में) कितना है?",
            "options": [
                {"id": "A", "text": "156100"},
                {"id": "B", "text": "155500"},
                {"id": "C", "text": "156250"},
                {"id": "D", "text": "158225"}
            ],
            "correct": "C",
            "solution": "Selling Price = MP × (100 - 44)% = MP × 56%\nMP × (56/100) = 87500\n⇒ MP = (87500 × 100) / 56 = 156250.",
            "trick": "MP = 87500 / 0.56 = 156250."
        },
        {
            "id": 8,
            "topic": "Time & Work",
            "exam": "SSC CGL Tier-II, 19/01/2026",
            "question_en": "P and Q can complete a task in 20 days and 30 days respectively. They work together for 6 days, then Q is replaced by R. If the remaining work is completed by P and R together in 8 more days, in how many days can R alone complete 60% of the work?",
            "question_hi": "P और Q एक काम को क्रमशः 20 दिन और 30 दिन में कर सकते हैं। वे 6 दिनों तक एक साथ काम करते हैं, और फिर Q की जगह R आ जाता है। अगर बचा हुआ काम P और R मिलकर 8 और दिनों में पूरा करते हैं, तो R अकेला उस काम का 60% कितने दिनों में पूरा कर सकता है?",
            "options": [
                {"id": "A", "text": "48 days"},
                {"id": "B", "text": "34 days"},
                {"id": "C", "text": "28 days"},
                {"id": "D", "text": "64 days"}
            ],
            "correct": "A",
            "solution": "Total work = LCM(20, 30) = 60 units.\nEfficiency of P = 3 units/day, Efficiency of Q = 2 units/day.\nWork done by P + Q in 6 days = (3 + 2) × 6 = 30 units.\nRemaining work = 60 - 30 = 30 units.\nP and R complete 30 units in 8 days ⇒ (Efficiency of P + Efficiency of R) × 8 = 30\n⇒ 3 + Efficiency of R = 30/8 = 3.75 ⇒ Efficiency of R = 0.75 = 3/4 unit/day.\n60% of total work = 60 × 0.60 = 36 units.\nTime for R alone = 36 / (3/4) = 48 days.",
            "trick": "R's rate = (30 - 3×8)/8 = 6/8 = 3/4 unit/day. 60% of 60 is 36. Days = 36 / 0.75 = 48."
        },
        {
            "id": 9,
            "topic": "Pipe & Cistern",
            "exam": "SSC CGL Tier-II, 19/01/2026",
            "question_en": "A hemispherical tank is filled with water. It is connected to a pipe that empties it at a rate of 7 liters per second. If the inner radius of the tank is 2.1 meters, how much time (in minutes) will it take to empty half of the tank? (Use π = 22/7 and 1 m³ = 1000 liters)",
            "question_hi": "एक अर्द्धगोला टैंक पानी से भरा है। यह एक पाइप से जुड़ा है जो इसे 7 लीटर प्रति सेकंड की दर से खाली करता है। अगर टैंक का अंदरूनी रेडियस 2.1 मीटर है, तो टैंक को आधा खाली करने में लगभग कितना समय (मिनट में) लगेगा? (π = 22/7 और 1 मीटर³ = 1000 लीटर)",
            "options": [
                {"id": "A", "text": "46 minutes"},
                {"id": "B", "text": "23 minutes"},
                {"id": "C", "text": "11 minutes"},
                {"id": "D", "text": "16 minutes"}
            ],
            "correct": "B",
            "solution": "Volume of hemisphere = (2/3) π r³.\nHalf volume = (1/3) π r³.\n= (1/3) × (22/7) × (2.1)³ m³ = (1/3) × (22/7) × 9.261 = 9.702 m³ = 9702 liters.\nEmptying rate = 7 liters/sec = 7 × 60 = 420 liters/min.\nTime = 9702 / 420 = 23.1 ≈ 23 minutes.",
            "trick": "Time = (1/3 × 22/7 × 2.1 × 2.1 × 2.1 × 1000) / (7 × 60) = 23 minutes."
        },
        {
            "id": 10,
            "topic": "Simple Interest",
            "exam": "SSC CGL Tier-II, 03/03/2023",
            "question_en": "What is the ratio of the simple interest earned on a certain sum of money at 21% per annum in 8 years to the simple interest earned on the same sum at the same rate for 21 years?",
            "question_hi": "एक निश्चित धनराशि पर 8 वर्ष में 21% वार्षिक दर से अर्जित साधारण ब्याज का उसी धनराशि पर 21 वर्ष में सामान दर से अर्जित साधारण ब्याज से अनुपात क्या है?",
            "options": [
                {"id": "A", "text": "21 : 5"},
                {"id": "B", "text": "21 : 8"},
                {"id": "C", "text": "8 : 21"},
                {"id": "D", "text": "5 : 21"}
            ],
            "correct": "C",
            "solution": "SI = (P × R × T) / 100.\nSince P and R are same in both cases:\nSI1 / SI2 = T1 / T2 = 8 / 21.\nRatio = 8 : 21.",
            "trick": "Direct ratio = 8 : 21 because SI ∝ Time when P and R are constant."
        },
        {
            "id": 11,
            "topic": "Compound Interest",
            "exam": "SSC CHSL Tier-II, 10/04/2026",
            "question_en": "A sum of money is invested at compound interest. The amount after 2 years is ₹15,972 and after 3 years it becomes ₹17,888.64. What is the rate of interest per annum?",
            "question_hi": "एक धनराशि को चक्रवृद्धि ब्याज पर निवेश किया गया है। 2 वर्षों के बाद राशि ₹15,972 है और 3 वर्षों के बाद यह ₹17,888.64 हो जाती है। प्रति वर्ष ब्याज दर क्या है?",
            "options": [
                {"id": "A", "text": "10%"},
                {"id": "B", "text": "12%"},
                {"id": "C", "text": "14%"},
                {"id": "D", "text": "16%"}
            ],
            "correct": "B",
            "solution": "Interest in the 3rd year = Amount after 3 yrs - Amount after 2 yrs\n= 17888.64 - 15972 = ₹1916.64.\nRate% = (1916.64 / 15972) × 100% = 12%.",
            "trick": "17888.64 / 15972 = 1.12 ⇒ R = 12%."
        },
        {
            "id": 12,
            "topic": "Average",
            "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "The average of 11 results is 59, and the average of the first 10 results is 58. What is the 11th result?",
            "question_hi": "11 परिणामों का औसत 59 है और पहले 10 परिणामों का औसत 58 है। 11वां परिणाम क्या है?",
            "options": [
                {"id": "A", "text": "68"},
                {"id": "B", "text": "58"},
                {"id": "C", "text": "69"},
                {"id": "D", "text": "59"}
            ],
            "correct": "C",
            "solution": "Sum of 11 results = 11 × 59 = 649.\nSum of first 10 results = 10 × 58 = 580.\n11th result = 649 - 580 = 69.",
            "trick": "11th result = 59 + 10 × (59 - 58) = 59 + 10 = 69."
        },
        {
            "id": 13,
            "topic": "Time, Speed & Distance",
            "exam": "SSC CGL Tier-II, 12/09/2019",
            "question_en": "A man starts from his house and travelling at 30km/h he reaches his office late by 10 minutes, and travelling at 24km/h he reaches his office late by 18 minutes. The distance (in km) from his house to his office is:",
            "question_hi": "एक आदमी अपने घर से 30 किमी/घंटा की गति से चलना शुरू करता है, वह अपने कार्यालय में 10 मिनट की देरी से पहुँचता है, और 24 किमी/घंटा की गति से यात्रा करके, वह 18 मिनट की देरी से अपने कार्यालय पहुंचता है। उसके घर से उसके कार्यालय की दूरी (किमी में) है:",
            "options": [
                {"id": "A", "text": "12 km"},
                {"id": "B", "text": "20 km"},
                {"id": "C", "text": "18 km"},
                {"id": "D", "text": "16 km"}
            ],
            "correct": "D",
            "solution": "Difference in time Δt = 18 - 10 = 8 minutes = 8/60 hour = 2/15 hour.\nDistance = (S1 × S2 / |S1 - S2|) × Δt\n= (30 × 24 / 6) × (2/15) = 120 × (2/15) = 16 km.",
            "trick": "D = (30 × 24 / 6) × (8/60) = 120 × 2/15 = 16 km."
        },
        {
            "id": 14,
            "topic": "Train",
            "exam": "SSC CGL Tier-II, 07/03/2023",
            "question_en": "A goods train 350 m long passes through a tunnel of length 1250 m in 80 seconds. What is the speed of the train?",
            "question_hi": "350 मीटर लंबी एक मालगाड़ी 1250 मीटर लंबी सुरंग से 80 सेकंड में गुजरती है। ट्रेन की गति क्या है?",
            "options": [
                {"id": "A", "text": "64 km/h"},
                {"id": "B", "text": "56 km/h"},
                {"id": "C", "text": "78 km/h"},
                {"id": "D", "text": "72 km/h"}
            ],
            "correct": "D",
            "solution": "Total distance = Length of train + Length of tunnel = 350 + 1250 = 1600 m.\nSpeed in m/s = 1600 / 80 = 20 m/s.\nSpeed in km/h = 20 × (18/5) = 72 km/h.",
            "trick": "Speed = (1600 / 80) × 18/5 = 20 × 18/5 = 72 km/h."
        },
        {
            "id": 15,
            "topic": "Boat & Stream",
            "exam": "SSC CGL Tier-II, 03/03/2023",
            "question_en": "A boat covers a distance of 35 km downstream in 2 hours and the same distance upstream in 7 hours. Find the speed (km/h) of the boat in still water?",
            "question_hi": "एक नाव धारा के अनुकूल 35 किमी की दूरी 2 घंटे में तय करती है और धारा के प्रतिकूल सामान दूरी 7 घंटे में तय करती है। शांत जल में नाव की चाल (किमी/घंटा) ज्ञात कीजिये?",
            "options": [
                {"id": "A", "text": "18.25 km/h"},
                {"id": "B", "text": "10.55 km/h"},
                {"id": "C", "text": "11.25 km/h"},
                {"id": "D", "text": "28.75 km/h"}
            ],
            "correct": "C",
            "solution": "Downstream speed D = 35 / 2 = 17.5 km/h.\nUpstream speed U = 35 / 7 = 5 km/h.\nSpeed of boat in still water = (D + U) / 2 = (17.5 + 5) / 2 = 22.5 / 2 = 11.25 km/h.",
            "trick": "Boat speed = (35/2 + 35/7)/2 = (17.5 + 5)/2 = 11.25 km/h."
        },
        {
            "id": 16,
            "topic": "Race",
            "exam": "SSC CGL Tier-II, 20/01/2025",
            "question_en": "P and Q take part in 400 m race. P runs at 12 km/hr. P gives Q a start of 20 m and still beats him by 13 seconds. The speed of Q is (rounded up to two decimal places):",
            "question_hi": "P और Q एक 400 मीटर की दौड़ में भाग लेते हैं। P, 12 किमी/घंटा की चाल से दौड़ता है। P, Q को 20 मीटर की बढ़त देता है और फिर भी उसे 13 सेकंड से हरा देता है। Q की चाल क्या है? (दो दशमलव स्थानों तक)",
            "options": [
                {"id": "A", "text": "11.38 km/hr"},
                {"id": "B", "text": "10.29 km/hr"},
                {"id": "C", "text": "11.61 km/hr"},
                {"id": "D", "text": "10.87 km/hr"}
            ],
            "correct": "B",
            "solution": "Speed of P = 12 × (5/18) = 10/3 m/s.\nTime taken by P to complete 400 m = 400 / (10/3) = 120 seconds.\nTime taken by Q = 120 + 13 = 133 seconds.\nDistance covered by Q = 400 - 20 = 380 m.\nSpeed of Q = 380 / 133 m/s = (380 / 133) × (18/5) = 72/7 ≈ 10.29 km/hr.",
            "trick": "Q's speed = (380 / 133) × 18/5 = 72/7 ≈ 10.29 km/hr."
        },
        {
            "id": 17,
            "topic": "Age",
            "exam": "SSC CGL Tier-II, 20/01/2025",
            "question_en": "The ratio of the ages of two friends is 4 : 3 which will become 6 : 5 after 4 years. What will be the sum of their ages (in years) after 22 years from now?",
            "question_hi": "दो मित्रों की आयु का अनुपात 4:3 है जो 4 वर्ष बाद 6:5 हो जायेगा। अब से 22 वर्ष बाद उनकी आयु का योग (वर्ष में) कितना होगा?",
            "options": [
                {"id": "A", "text": "56"},
                {"id": "B", "text": "58"},
                {"id": "C", "text": "52"},
                {"id": "D", "text": "50"}
            ],
            "correct": "B",
            "solution": "Present ratio = 4 : 3. After 4 years = 6 : 5.\nIncrease in ratio units = 6 - 4 = 2 units for 4 years ⇒ 1 unit = 2 years.\nPresent ages = 4 × 2 = 8 years and 3 × 2 = 6 years (Sum = 14 years).\nAfter 22 years, each age increases by 22 years:\nSum = 14 + 22 + 22 = 58 years.",
            "trick": "2 units = 4 years ⇒ 1 unit = 2. Present sum = 7 units = 14. After 22 yrs = 14 + 44 = 58."
        },
        {
            "id": 18,
            "topic": "Number System",
            "exam": "SSC CGL Tier-II, 20/01/2025",
            "question_en": "Which number among 38211, 38121, 32118, and 31128 is divisible by 24?",
            "question_hi": "38211, 38121, 32118 और 31128 में से कौन-सी संख्या 24 से विभाज्य है?",
            "options": [
                {"id": "A", "text": "32118"},
                {"id": "B", "text": "31128"},
                {"id": "C", "text": "38121"},
                {"id": "D", "text": "38211"}
            ],
            "correct": "B",
            "solution": "For divisibility by 24 = 3 × 8:\n1) Must be divisible by 8 (last 3 digits divisible by 8).\n- 38211 and 38121 are odd, so not divisible by 8.\n- 32118: last 3 digits 118 / 8 = 14.75 (Not divisible by 8).\n- 31128: last 3 digits 128 / 8 = 16 (Divisible by 8).\n2) Check divisibility by 3 for 31128: Sum of digits = 3 + 1 + 1 + 2 + 8 = 15 (Divisible by 3).\nHence, 31128 is divisible by 24.",
            "trick": "Only 31128 ends in 128 (128 is multiple of 8) and digit sum 15 is multiple of 3."
        },
        {
            "id": 19,
            "topic": "Number System",
            "exam": "SSC CGL Tier-II, 13/09/2019",
            "question_en": "What is the remainder when (127^97 + 97^97) is divided by 32?",
            "question_hi": "जब (127^97 + 97^97) को 32 से विभाजित किया जाता है तो कितना शेषफल बचता है?",
            "options": [
                {"id": "A", "text": "7"},
                {"id": "B", "text": "2"},
                {"id": "C", "text": "4"},
                {"id": "D", "text": "0"}
            ],
            "correct": "D",
            "solution": "For any odd integer n, (a^n + b^n) is always divisible by (a + b).\nHere n = 97 (odd), so (127^97 + 97^97) is divisible by (127 + 97) = 224.\nSince 224 = 32 × 7, 224 is a multiple of 32.\nTherefore, (127^97 + 97^97) is completely divisible by 32, leaving remainder 0.",
            "trick": "(127 + 97) = 224. 224 / 32 = 7 remainder 0."
        },
        {
            "id": 20,
            "topic": "Algebra",
            "exam": "SSC CGL Tier-II, 06/03/2023",
            "question_en": "If 4x² + y² = 40 and xy = 6, then find the positive value of 2x + y.",
            "question_hi": "यदि 4x² + y² = 40 और xy = 6, तो 2x + y का मान ज्ञात कीजिये?",
            "options": [
                {"id": "A", "text": "8"},
                {"id": "B", "text": "6"},
                {"id": "C", "text": "4"},
                {"id": "D", "text": "5"}
            ],
            "correct": "A",
            "solution": "(2x + y)² = (2x)² + y² + 2(2x)(y)\n= 4x² + y² + 4xy\n= 40 + 4(6) = 40 + 24 = 64\n⇒ 2x + y = √64 = 8.",
            "trick": "(2x + y)² = 40 + 4(6) = 64 ⇒ 8."
        },
        {
            "id": 21,
            "topic": "Trigonometry",
            "exam": "SSC CGL Tier-II, 19/01/2026",
            "question_en": "What is the value of (3/2) × (cos 39° / sin 51°) – √(sin² 39° + sin² 51°)?",
            "question_hi": "(3/2) × (cos 39° / sin 51°) – √(sin² 39° + sin² 51°) का मान क्या होगा?",
            "options": [
                {"id": "A", "text": "7/8"},
                {"id": "B", "text": "1/2"},
                {"id": "C", "text": "5/6"},
                {"id": "D", "text": "3/2"}
            ],
            "correct": "B",
            "solution": "cos 39° = sin(90° - 39°) = sin 51° ⇒ cos 39° / sin 51° = 1.\nsin² 51° = cos² 39° ⇒ sin² 39° + sin² 51° = sin² 39° + cos² 39° = 1.\nExpression = (3/2) × (1) – √1 = 3/2 – 1 = 1/2.",
            "trick": "3/2 × 1 - √1 = 1.5 - 1 = 0.5 = 1/2."
        },
        {
            "id": 22,
            "topic": "Geometry",
            "exam": "SSC CHSL Tier-II, 10/01/2024",
            "question_en": "In △XYZ, if XY = 5 cm, XZ = 7 cm and Q is a point on YZ such that XQ bisects ∠X, then YQ : QZ is:",
            "question_hi": "△XYZ में, यदि XY = 5cm, XZ = 7cm और Q, YZ पर एक बिंदु इस प्रकार है कि XQ, ∠X को समद्विभाजित करता है, तो YQ : QZ का मान ज्ञात कीजिए।",
            "options": [
                {"id": "A", "text": "5 : 7"},
                {"id": "B", "text": "7 : 12"},
                {"id": "C", "text": "7 : 5"},
                {"id": "D", "text": "5 : 12"}
            ],
            "correct": "A",
            "solution": "By the Angle Bisector Theorem:\nThe angle bisector of an angle of a triangle divides the opposite side into segments proportional to the adjacent sides.\nYQ / QZ = XY / XZ = 5 / 7.\nHence, YQ : QZ = 5 : 7.",
            "trick": "Direct theorem: YQ : QZ = XY : XZ = 5 : 7."
        },
        {
            "id": 23,
            "topic": "Mensuration 2D",
            "exam": "SSC CGL Tier-II, 19/01/2026",
            "question_en": "A rectangle has an area of 48 cm² and a perimeter of 28 cm. If a rhombus is formed by joining the midpoints of its sides, what is the area of the rhombus?",
            "question_hi": "एक आयत ऐसा है कि उसका क्षेत्रफल 48 सेमी² है और इसका परिमाप 28 सेमी है। अगर इस आयत की भुजाओं के मध्यबिंदु को मिलाकर एक समचतुर्भुज बनाया जाता है, तो उस समचतुर्भुज का क्षेत्रफल क्या होगा?",
            "options": [
                {"id": "A", "text": "20 cm²"},
                {"id": "B", "text": "48 cm²"},
                {"id": "C", "text": "12 cm²"},
                {"id": "D", "text": "24 cm²"}
            ],
            "correct": "D",
            "solution": "The quadrilateral formed by joining the midpoints of the sides of any rectangle is always a rhombus.\nThe diagonals of this rhombus are equal to the length and breadth of the rectangle (d1 = l, d2 = b).\nArea of rhombus = (1/2) × d1 × d2 = (1/2) × l × b = (1/2) × (Area of rectangle)\n= (1/2) × 48 = 24 cm².",
            "trick": "Area of inscribed midpoint rhombus = (Area of Rectangle) / 2 = 48 / 2 = 24 cm²."
        },
        {
            "id": 24,
            "topic": "Statistics",
            "exam": "SSC CHSL Tier-2, 26/06/2023",
            "question_en": "Find the median of the following data: 15, 30, 20, 10, 25, 35, 18, 21, 28.",
            "question_hi": "निम्नलिखित आँकड़ों की माध्यिका ज्ञात कीजिए: 15, 30, 20, 10, 25, 35, 18, 21, 28",
            "options": [
                {"id": "A", "text": "18"},
                {"id": "B", "text": "25"},
                {"id": "C", "text": "30"},
                {"id": "D", "text": "21"}
            ],
            "correct": "D",
            "solution": "Arranging the numbers in ascending order:\n10, 15, 18, 20, 21, 25, 28, 30, 35\nTotal terms n = 9 (odd).\nMedian = ((n + 1)/2)th term = ((9 + 1)/2)th term = 5th term.\n5th term = 21.",
            "trick": "Middle item of 9 values sorted is the 5th item: 10, 15, 18, 20, [21], 25, 28, 30, 35 ⇒ 21."
        },
        {
            "id": 25,
            "topic": "Probability",
            "exam": "SSC CGL Tier-II, 02/03/2023",
            "question_en": "A glass vessel contains 6 white, 8 black, 4 red and 3 blue marbles. If one glass is selected at random from the vessel, what is the probability that it is black or blue?",
            "question_hi": "एक कांच के पात्र में 6 सफ़ेद, 8 काले, 4 लाल और 3 नीले कंचे हैं। यदि पात्र में से एक कंचा यादृच्छिक रूप से चुना जाता है, तो इसके काले या नीले रंग के होने की प्रायिकता क्या है?",
            "options": [
                {"id": "A", "text": "5/21"},
                {"id": "B", "text": "1/7"},
                {"id": "C", "text": "8/21"},
                {"id": "D", "text": "11/21"}
            ],
            "correct": "D",
            "solution": "Total marbles = 6 + 8 + 4 + 3 = 21.\nFavorable marbles (black or blue) = 8 + 3 = 11.\nProbability = 11 / 21.",
            "trick": "P(Black or Blue) = (8 + 3) / 21 = 11/21."
        }
    ]
}

with open("app/data/tests/cgl-mains-mock-01.json", "w", encoding="utf-8") as f:
    json.dump(test_1, f, indent=2, ensure_ascii=False)

print("Created cgl-mains-mock-01.json successfully!")

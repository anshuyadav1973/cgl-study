import json
import os

tests_dir = "app/data/tests"

# Test 07: Commercial Maths: Profit, Loss, Discount, Simple & Compound Interest (25 Questions)
test_7 = {
    "id": "cgl-mains-mock-07",
    "title": "SSC CGL Mains 2026 - Commercial Maths: Profit/Loss & SI/CI (25 Qs)",
    "subtitle": "Successive Discounts, Dishonest Dealer, Installments, Half-yearly Compounding",
    "category": "Commercial Maths",
    "durationMinutes": 35,
    "marksPerQuestion": 3,
    "negativeMarks": 1,
    "instructions": ["25 Questions covering Profit & Loss, Successive Discounts, Simple Interest & Compound Interest.", "Tier-2 Marking: +3 correct, -1 wrong."],
    "questions": [
        {
            "id": 1, "topic": "Profit & Loss", "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "Sandeep earns 22% profit by selling an overcoat for ₹8540. Find the cost price of overcoat.",
            "question_hi": "संदीप एक ओवरकोट को ₹8540 में बेचकर 22% लाभ अर्जित करता है। ओवरकोट का क्रयमूल्य ज्ञात कीजिये?",
            "options": [{"id":"A","text":"₹6500"},{"id":"B","text":"₹7000"},{"id":"C","text":"₹7500"},{"id":"D","text":"₹6000"}],
            "correct": "B",
            "solution": "SP = 122% of CP = ₹8540.\nCP = (8540 / 122) × 100 = 70 × 100 = ₹7000.",
            "trick": "8540 / 1.22 = ₹7000."
        },
        {
            "id": 2, "topic": "Profit & Loss", "exam": "SSC CHSL (Tier-I), 16/03/2023",
            "question_en": "A trader buys two articles for ₹3000 each article. While selling, he earns a profit of 10 percent on one and loses 20 percent on the other. What will be his overall loss percentage?",
            "question_hi": "एक व्यापारी ₹3000 प्रति वस्तु के हिसाब से दो वस्तुएँ खरीदता है। बेचते समय, वह एक वस्तु पर 10 प्रतिशत का लाभ कमाता है और दूसरे पर 20 प्रतिशत की हानि करता है। उसका कुल हानि प्रतिशत कितना होगा?",
            "options": [{"id":"A","text":"10%"},{"id":"B","text":"20%"},{"id":"C","text":"15%"},{"id":"D","text":"5%"}],
            "correct": "D",
            "solution": "When Cost Price (CP) is the same for both articles:\nNet profit/loss% = (Profit% + Loss%) / 2 = (10% - 20%) / 2 = -10% / 2 = -5% (5% Loss).",
            "trick": "Same CP ⇒ Average of percentages = (10 - 20)/2 = -5%."
        },
        {
            "id": 3, "topic": "Profit & Loss", "exam": "SSC CGL Tier-II, 26/10/2023",
            "question_en": "B purchased 15 kg apples at the rate of ₹180 per kg from a wholesaler who uses a weight of 950 grams for the 1kg weight. B sold all these apples at ₹180 per kg but used a weight of 750 grams for the kg weight. Find the percentage profit earned by B in the transaction (correct to 2 places of decimal).",
            "question_hi": "B ने एक थोक विक्रेता से ₹180 प्रति किग्रा की दर से 15 किग्रा सेब खरीदे, जो एक किग्रा वज़न के लिए 950 ग्राम के वज़न का उपयोग करता है। B ने इन सभी सेबों को ₹180 प्रति किग्रा की दर से बेचा, लेकिन एक किग्रा वज़न के लिए 750 ग्राम के वज़न का उपयोग किया। इस लेन-देन में B द्वारा अर्जित लाभ प्रतिशत ज्ञात कीजिए:",
            "options": [{"id":"A","text":"25.75%"},{"id":"B","text":"26.67%"},{"id":"C","text":"22.55%"},{"id":"D","text":"33.33%"}],
            "correct": "B",
            "solution": "Effective ratio of goods: B bought 950g for price of 1000g, and sells 750g for price of 1000g.\nProfit ratio = 950 / 750 = 19 / 15.\nProfit% = (19 - 15) / 15 × 100% = 4/15 × 100% = 26.67%.",
            "trick": "Profit% = (950 - 750)/750 × 100% = 200/750 × 100% = 26.67%."
        },
        {
            "id": 4, "topic": "Profit & Loss", "exam": "CDS Maths, 08/09/2019",
            "question_en": "A trader sells two computers at the same price, making a profit of 30% on one and a loss of 30% on the other. What is the net loss or profit percentage on the transaction?",
            "question_hi": "एक व्यापारी दो कंप्यूटरों को एक ही कीमत पर बेचता है, जिसमें से उसे एक पर 30% का लाभ होता है और दूसरे पर 30% की हानि होती है। इस लेनदेन में कितने प्रतिशत शुद्ध लाभ या हानि हुई?",
            "options": [{"id":"A","text":"6% Loss"},{"id":"B","text":"6% Profit"},{"id":"C","text":"9% Loss"},{"id":"D","text":"9% Profit"}],
            "correct": "C",
            "solution": "When selling price is same and profit% = loss% = x%:\nAlways a net loss = x² / 100% = 30² / 100% = 9% Loss.",
            "trick": "30² / 100 = 9% Loss."
        },
        {
            "id": 5, "topic": "Profit & Loss", "exam": "SSC SELECTION PHASE HIGHER LEVEL 2026",
            "question_en": "A shopkeeper earns a profit of 19% on the cost price of an article after giving three consecutive discounts of 11%, 13% and 15% to a customer. What would have been the profit percentage, had the shopkeeper given discounts of 11% and 13% only?",
            "question_hi": "एक दुकानदार किसी वस्तु के लागत मूल्य पर 19% का लाभ अर्जित करता है, जब वह ग्राहक को क्रमशः 11%, 13% और 15% की तीन क्रमिक छूट देता है। यदि दुकानदार केवल 11% और 13% की ही छूट देता, तो उसका लाभ प्रतिशत क्या होता?",
            "options": [{"id":"A","text":"35%"},{"id":"B","text":"40%"},{"id":"C","text":"45%"},{"id":"D","text":"50%"}],
            "correct": "B",
            "solution": "Let CP = 100. Then SP1 = 119.\nSP1 is obtained after discounts 11%, 13%, and 15% (which is a multiplier of (1 - 0.15) = 0.85 = 17/20 on the intermediate price after 11% and 13% discounts).\nTherefore, SP2 (with only 11% and 13% discounts) = 119 / 0.85 = 119 / (17/20) = 7 × 20 = 140.\nProfit with only first two discounts = 140 - 100 = 40%.",
            "trick": "SP2 = 119 / 0.85 = 140 ⇒ Profit = 40%."
        },
        {
            "id": 6, "topic": "Profit & Loss", "exam": "SSC SELECTION PHASE GRADUATE LEVEL 2026",
            "question_en": "A seller offers a 20% discount and still earns a 25% profit. If the profit made is ₹75, find the marked price of the article.",
            "question_hi": "एक विक्रेता 20% की छूट देता है और फिर भी 25% का लाभ कमाता है। यदि अर्जित लाभ ₹75 है, तो वस्तु का अंकित मूल्य ज्ञात कीजिए।",
            "options": [{"id":"A","text":"₹504.25"},{"id":"B","text":"₹468.75"},{"id":"C","text":"₹490.00"},{"id":"D","text":"₹570.00"}],
            "correct": "B",
            "solution": "25% of CP = ₹75 ⇒ CP = 75 × 4 = ₹300.\nSelling Price SP = 300 + 75 = ₹375.\nSince discount is 20%: SP = 80% of MP ⇒ MP = 375 / 0.80 = ₹468.75.",
            "trick": "MP = (300 × 1.25) / 0.80 = 375 / 0.8 = ₹468.75."
        },
        {
            "id": 7, "topic": "Profit & Loss", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "A scheme offers “Buy 3, Get 2 free” on the same kind of articles with equal marked price. Find the effective discount percentage.",
            "question_hi": "एक योजना समान प्रकार की वस्तुओं पर, जिनका अंकित मूल्य समान है, “3 खरीदो, 2 निःशुल्क पाओ” की पेशकश करती है। प्रभावी छूट प्रतिशत ज्ञात कीजिए।",
            "options": [{"id":"A","text":"32%"},{"id":"B","text":"36%"},{"id":"C","text":"40%"},{"id":"D","text":"45%"}],
            "correct": "C",
            "solution": "Free items = 2. Total items taken = 3 + 2 = 5.\nEffective discount% = (2 / 5) × 100% = 40%.",
            "trick": "2 / 5 = 40%."
        },
        {
            "id": 8, "topic": "Profit & Loss", "exam": "SSC CHSL Tier-II, 10/01/2023",
            "question_en": "Sohan sells sugar at cost price but uses a faulty weight and thereby gains 28%. How many grams of sugar does he give in place of 3.2 kg?",
            "question_hi": "सोहन क्रय मूल्य पर चीनी बेचता है लेकिन वह खराब बांटों का प्रयोग करता है और इस प्रकार 28% का लाभ अर्जित करता है। वह 3.2 किग्रा चीनी के बदले कितने ग्राम चीनी दे रहा है?",
            "options": [{"id":"A","text":"1500 g"},{"id":"B","text":"1900 g"},{"id":"C","text":"2200 g"},{"id":"D","text":"2500 g"}],
            "correct": "D",
            "solution": "28% profit = 28/100 = 7/25 ⇒ Ratio of SP/CP = 32/25.\nClaimed weight = 3.2 kg = 3200 g (corresponds to 32 units).\nActual weight given = 25 units = (3200 / 32) × 25 = 2500 grams.",
            "trick": "3200 / 1.28 = 2500 g."
        },
        {
            "id": 9, "topic": "Discount", "exam": "SSC CGL Tier-II, 07/03/2023",
            "question_en": "At a clearance sale, a shopkeeper gives 45% discount. If a customer paid ₹330 during the sale, then what is the marked price of that shirt?",
            "question_hi": "निकासी बिक्री पर, एक दुकानदार 45% छूट देता है। यदि एक ग्राहक ने बिक्री के दौरान ₹330 का भुगतान किया, तो उस शर्ट का अंकित मूल्य क्या है?",
            "options": [{"id":"A","text":"₹550"},{"id":"B","text":"₹600"},{"id":"C","text":"₹500"},{"id":"D","text":"₹650"}],
            "correct": "B",
            "solution": "SP = MP × (100 - 45)% = 55% of MP = ₹330.\nMP = (330 / 55) × 100 = 6 × 100 = ₹600.",
            "trick": "330 / 0.55 = ₹600."
        },
        {
            "id": 10, "topic": "Discount", "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "On the occasion of Republic Day, a retail store offers a scheme where customers can avail a discount of 26% on their total purchase. If Manish buys items worth ₹2,050, how much money (in ₹) will he save through the scheme discount?",
            "question_hi": "गणतंत्र दिवस के अवसर पर एक खुदरा स्टोर एक स्कीम देता है, जहाँ ग्राहक अपनी कुल खरीद पर 26% की छूट का लाभ उठा सकते हैं। यदि मनीष ₹2,050 की वस्तुएँ खरीदता है, तो वह स्कीम छूट के द्वारा कितनी राशि (₹ में) बचाएगा?",
            "options": [{"id":"A","text":"₹533"},{"id":"B","text":"₹544"},{"id":"C","text":"₹522"},{"id":"D","text":"₹511"}],
            "correct": "A",
            "solution": "Savings = 26% of ₹2050 = (26 / 100) × 2050 = 26 × 20.5 = ₹533.",
            "trick": "2050 × 0.26 = 533."
        },
        {
            "id": 11, "topic": "Discount", "exam": "SSC CHSL Tier-II, 02/11/2023",
            "question_en": "For an electric bill for ₹50,000, what is the difference between a discount of 30% and two successive discounts of 26% and 5%?",
            "question_hi": "₹50,000 के बिजली बिल के लिए, 30% की छूट और 26% एवं 5% की दो क्रमिक छूटों के बीच अंतर ज्ञात कीजिए।",
            "options": [{"id":"A","text":"₹140"},{"id":"B","text":"₹150"},{"id":"C","text":"₹130"},{"id":"D","text":"₹120"}],
            "correct": "B",
            "solution": "Single discount = 30%.\nTwo successive discounts of 26% and 5% = 26 + 5 - (26 × 5)/100 = 31 - 1.30 = 29.7%.\nDifference in percentage = 30% - 29.7% = 0.3%.\nDifference in amount = 0.3% of 50,000 = (0.3 / 100) × 50,000 = ₹150.",
            "trick": "(30 - 29.7)% of 50000 = 0.3% of 50000 = ₹150."
        },
        {
            "id": 12, "topic": "Discount", "exam": "SSC CHSL Tier-II, 02/11/2023",
            "question_en": "A shopkeeper sold his goods at half the list price and thus lost 17%. If he had sold on the listed price, then his gain percentage would be:",
            "question_hi": "एक दुकानदार ने अपना माल अंकित मूल्य से आधे दाम पर बेचा और इस प्रकार उसे 17% की हानि हुई। यदि उसने अपना माल अंकित मूल्य पर बेचा होता, तो उसकी लाभ प्रतिशतता कितनी होती?",
            "options": [{"id":"A","text":"17%"},{"id":"B","text":"41%"},{"id":"C","text":"83%"},{"id":"D","text":"66%"}],
            "correct": "D",
            "solution": "Let CP = 100. Since he lost 17%, SP = 83.\nSP is half of list price (MP) ⇒ MP = 83 × 2 = 166.\nSelling at listed price yields SP = 166.\nGain% = (166 - 100)% = 66%.",
            "trick": "MP = 2 × 83 = 166 ⇒ Profit = 66%."
        },
        {
            "id": 13, "topic": "Discount", "exam": "SSC CGL Tier-II, 26/10/2023",
            "question_en": "A merchant fixes the sale price of his goods at 42% above the cost price. He sells his goods at a 15% discount on marked price. His percentage of profit (rounded off to the nearest integer) is:",
            "question_hi": "एक व्यापारी अपने माल का विक्रय मूल्य, क्रय मूल्य से 42% अधिक अंकित करता है। वह अपना माल अंकित मूल्य पर 15% छूट देकर बेचता है। उसका लाभ प्रतिशत (निकटतम पूर्णांक तक) कितना है?",
            "options": [{"id":"A","text":"21%"},{"id":"B","text":"35%"},{"id":"C","text":"27%"},{"id":"D","text":"42%"}],
            "correct": "A",
            "solution": "Net change% = a + b + (ab/100) = 42 - 15 - (42 × 15)/100 = 27 - 6.30 = 20.7% ≈ 21%.",
            "trick": "1.42 × 0.85 = 1.207 ⇒ 20.7% ≈ 21%."
        },
        {
            "id": 14, "topic": "Simple Interest", "exam": "SSC CGL Tier-II, 18/11/2024",
            "question_en": "Find the simple interest (in ₹) on ₹2000 at 6.5% per annum rate of interest for the period from 14 February 2023 to 28 April 2023.",
            "question_hi": "₹2000 पर, 6.5% वार्षिक ब्याज दर पर, 14 फरवरी 2023 से 28 अप्रैल 2023 की अवधि के लिए साधारण ब्याज (₹ में) की गणना करें।",
            "options": [{"id":"A","text":"₹24"},{"id":"B","text":"₹27"},{"id":"C","text":"₹26"},{"id":"D","text":"₹25"}],
            "correct": "C",
            "solution": "Days: Feb (28 - 14) = 14 days, March = 31 days, April = 28 days.\nTotal days = 14 + 31 + 28 = 73 days = 73 / 365 year = 1/5 year.\nSI = (2000 × 6.5 × 1/5) / 100 = (400 × 6.5) / 100 = ₹26.",
            "trick": "73 days = 1/5 yr. SI = 2000 × 0.065 / 5 = ₹26."
        },
        {
            "id": 15, "topic": "Simple Interest", "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "At 5% annual simple interest a sum amounts to ₹4160 in 6 years. Find the sum.",
            "question_hi": "5% वार्षिक साधारण ब्याज दर से एक राशि 6 वर्षों में ₹4160 हो जाती है। राशि ज्ञात कीजिये?",
            "options": [{"id":"A","text":"₹3200"},{"id":"B","text":"₹2900"},{"id":"C","text":"₹2800"},{"id":"D","text":"₹3100"}],
            "correct": "A",
            "solution": "Amount A = P(1 + RT/100) = P(1 + 30/100) = 1.30 P.\n1.30 P = 4160 ⇒ P = 4160 / 1.30 = ₹3200.",
            "trick": "4160 / 1.3 = ₹3200."
        },
        {
            "id": 16, "topic": "Simple Interest", "exam": "SSC CGL Tier-II, 02/03/2023",
            "question_en": "The difference between the simple interest of two banks on ₹8000 in 3 years is ₹800. If the rate of interest per annum in two banks is R1 and R2, then what is the value of R1 – R2? (where R1 > R2)",
            "question_hi": "3 वर्ष में ₹8000 पर दो बैंकों के साधारण ब्याज का अंतर ₹800 है। यदि दो बैंकों में ब्याज की प्रतिवर्ष दर R1 और R2 है, तो R1–R2 का मान क्या है? (जहाँ R1 > R2)",
            "options": [{"id":"A","text":"2 1/3%"},{"id":"B","text":"1 1/3%"},{"id":"C","text":"3 1/3%"},{"id":"D","text":"5 1/3%"}],
            "correct": "C",
            "solution": "Difference in SI = [P × (R1 - R2) × T] / 100\n800 = [8000 × (R1 - R2) × 3] / 100 = 240 (R1 - R2)\n⇒ R1 - R2 = 800 / 240 = 10 / 3 = 3 1/3%.",
            "trick": "(800 / (8000 × 3)) × 100 = 800 / 240 = 10/3 = 3 1/3%."
        },
        {
            "id": 17, "topic": "Simple Interest", "exam": "SSC CHSL Tier-II, 10/04/2026",
            "question_en": "A sum of money amounts to ₹12,000 in 5 years and ₹14,400 in 9 years at simple interest. What is the principal?",
            "question_hi": "साधारण ब्याज पर, कोई धनराशि 5 वर्षों में ₹12,000 और 9 वर्षों में ₹14,400 हो जाती है। मूलधन कितना है?",
            "options": [{"id":"A","text":"₹8000"},{"id":"B","text":"₹9000"},{"id":"C","text":"₹10000"},{"id":"D","text":"₹10500"}],
            "correct": "B",
            "solution": "Interest for 4 years (9 - 5) = 14400 - 12000 = ₹2400.\nInterest for 1 year = 2400 / 4 = ₹600.\nInterest for 5 years = 600 × 5 = ₹3000.\nPrincipal P = Amount after 5 yrs - 5 yrs Interest = 12000 - 3000 = ₹9000.",
            "trick": "P = 12000 - 5 × (2400 / 4) = 12000 - 3000 = ₹9000."
        },
        {
            "id": 18, "topic": "Simple Interest", "exam": "SSC SELECTION PHASE GL 2026",
            "question_en": "A sum of ₹15,600 is invested in a scheme of simple interest. The person receives ₹4,680 as interest after 3 years. If he had invested the same sum for 5 years at a rate 2% lower than the original rate, what would be the interest?",
            "question_hi": "₹15,600 की एक धनराशि साधारण ब्याज की एक योजना में निवेश की जाती है। 3 वर्षों के बाद व्यक्ति को ₹4,680 ब्याज के रूप में प्राप्त होते हैं। यदि वही धनराशि 5 वर्षों के लिए मूल दर से 2% कम दर पर निवेश की जाती, तो कितना ब्याज प्राप्त होता?",
            "options": [{"id":"A","text":"₹6,240"},{"id":"B","text":"₹5,400"},{"id":"C","text":"₹6,500"},{"id":"D","text":"₹5,850"}],
            "correct": "A",
            "solution": "Original SI for 1 year = 4680 / 3 = ₹1560.\nOriginal Rate R = (1560 / 15600) × 100% = 10%.\nNew Rate = 10% - 2% = 8%.\nNew SI for 5 years = (15600 × 8 × 5) / 100 = 156 × 40 = ₹6,240.",
            "trick": "New SI = 15600 × 40% = ₹6,240."
        },
        {
            "id": 19, "topic": "Compound Interest",
            "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "If a sum increases by 40% in 4 years at simple interest, then what will be the compound interest on ₹80000 after 4 years at the same interest rate?",
            "question_hi": "यदि किसी राशि में साधारण ब्याज पर 4 वर्ष में 40% की वृद्धि होती है, तो सामान ब्याज दर पर 4 वर्ष बाद ₹80000 पर चक्रवृद्धि ब्याज क्या होगा?",
            "options": [{"id":"A","text":"₹29728"},{"id":"B","text":"₹39724"},{"id":"C","text":"₹17128"},{"id":"D","text":"₹37128"}],
            "correct": "D",
            "solution": "Simple interest rate R = 40% / 4 = 10% per annum.\nCI rate for 4 years at 10% = 46.41%.\nCI = 46.41% of 80000 = (46.41 / 100) × 80000 = 46.41 × 800 = ₹37,128.",
            "trick": "Effective 4-year CI at 10% = 46.41%. 80000 × 0.4641 = ₹37128."
        },
        {
            "id": 20, "topic": "Compound Interest",
            "exam": "SSC CGL Tier-II, 03/03/2023",
            "question_en": "What will be the compound interest on an amount of ₹25000 after three years at 12% per annum, when the interest is compounded annually?",
            "question_hi": "₹25000 की राशि पर तीन वर्ष बाद 12% वार्षिक दर से चक्रवृद्धि ब्याज कितना होगा, जब ब्याज वार्षिक रूप से चक्रवृद्धि होता है?",
            "options": [{"id":"A","text":"₹9824.00"},{"id":"B","text":"₹10520.00"},{"id":"C","text":"₹10123.20"},{"id":"D","text":"₹10132.20"}],
            "correct": "C",
            "solution": "Using 3 : 3 : 1 ratio method:\nYear 1: 12% of 25000 = 3000\nYear 2: 12% of 3000 = 360\nYear 3: 12% of 360 = 43.2\nTotal CI = 3 × 3000 + 3 × 360 + 1 × 43.2 = 9000 + 1080 + 43.2 = ₹10,123.20.",
            "trick": "3(3000) + 3(360) + 43.2 = ₹10123.20."
        },
        {
            "id": 21, "topic": "Compound Interest",
            "exam": "SSC CGL Tier-II, 02/03/2023",
            "question_en": "If the interest is compounded half yearly, then find the compound interest on an amount of ₹8000 at the rate of 20% per annum for 1 year.",
            "question_hi": "यदि ब्याज अर्धवार्षिक रूप से चक्रवृद्धि होता है, तो ₹8000 की राशि पर 20% वार्षिक की दर से 1 वर्ष का चक्रवृद्धि ब्याज ज्ञात करें?",
            "options": [{"id":"A","text":"₹1685"},{"id":"B","text":"₹1675"},{"id":"C","text":"₹1690"},{"id":"D","text":"₹1680"}],
            "correct": "D",
            "solution": "Half-yearly rate = 20% / 2 = 10%. Periods n = 2.\nEffective CI% = 10 + 10 + (10 × 10)/100 = 21%.\nCI = 21% of 8000 = 21 × 80 = ₹1680.",
            "trick": "8000 × 21% = ₹1680."
        },
        {
            "id": 22, "topic": "Compound Interest",
            "exam": "SSC CGL Tier-II, 29/01/2022",
            "question_en": "A sum of money becomes ₹11,880 after 4 years and ₹17,820 after 6 years on compound interest, the interest is compounded annually. What is half of the sum (in ₹)?",
            "question_hi": "एक धनराशि वार्षिक रूप से चक्रवृद्धि होने वाले चक्रवृद्धि ब्याज पर, 4 वर्ष के बाद ₹11,880 और 6 वर्ष के बाद ₹17,820 हो जाती है। उस धनराशि का आधा भाग (₹ में) कितना होगा?",
            "options": [{"id":"A","text":"2,750"},{"id":"B","text":"2,530"},{"id":"C","text":"2,640"},{"id":"D","text":"2,410"}],
            "correct": "C",
            "solution": "Ratio in 2 years = 17820 / 11880 = 3/2.\nSo P × (3/2)² = 11880 ⇒ P × (9/4) = 11880\n⇒ P = (11880 × 4) / 9 = 1320 × 4 = ₹5280.\nHalf of the sum = 5280 / 2 = ₹2640.",
            "trick": "Half sum = 5280 / 2 = ₹2640."
        },
        {
            "id": 23, "topic": "Compound Interest",
            "exam": "SSC CGL Tier-II, 18/09/2020",
            "question_en": "At what rate per cent per annum will a sum of ₹15,625 amount to ₹21,952 in three years, if the interest is compounded annually?",
            "question_hi": "₹15,625 की धनराशि, वार्षिक रूप से चक्रवृद्धि किये जाने वाले कितने प्रतिशत ब्याज दर पर 3 वर्षों में ₹21,952 हो जाएगी?",
            "options": [{"id":"A","text":"12%"},{"id":"B","text":"8%"},{"id":"C","text":"9%"},{"id":"D","text":"10%"}],
            "correct": "A",
            "solution": "∛(21952 / 15625) = 28 / 25.\nRate = (28 - 25) / 25 × 100% = 3/25 × 100% = 12%.",
            "trick": "∛21952 = 28, ∛15625 = 25 ⇒ 3/25 = 12%."
        },
        {
            "id": 24, "topic": "Compound Interest",
            "exam": "SSC CGL Tier-II, 07/03/2023",
            "question_en": "Rajnish borrowed ₹1500 from a bank and repaid the entire amount with interest in two equal annual installments, the first installment being paid a year after Rajnish borrowed from the bank. If the rate of interest was 40% per annum, compounded annually, then what was the value (in ₹) of each installment paid by Rajnish?",
            "question_hi": "रजनीश ने एक बैंक से ₹1500 उधार लिए और दो समान वार्षिक किस्तों में ब्याज सहित पूरी राशि चुका दी, रजनीश द्वारा बैंक से उधार लेने के एक साल बाद पहली किस्त का भुगतान किया गया। यदि ब्याज की दर 40% प्रति वर्ष थी, जो वार्षिक रूप से संयोजित होती है, तो रजनीश द्वारा भुगतान की गई प्रत्येक किस्त का मूल्य (₹ में) क्या था?",
            "options": [{"id":"A","text":"1125"},{"id":"B","text":"1470"},{"id":"C","text":"1225"},{"id":"D","text":"1350"}],
            "correct": "C",
            "solution": "Rate = 40% = 2/5 ⇒ Multiplier = 7/5.\nInstallment formula: P = x / (7/5) + x / (7/5)² = (5/7)x + (25/49)x = (60/49)x.\n1500 = (60/49)x ⇒ x = (1500 × 49) / 60 = 25 × 49 = ₹1225.",
            "trick": "Installment must be a multiple of 7² = 49. Only 1225 is divisible by 49 (49 × 25 = 1225)."
        },
        {
            "id": 25, "topic": "Compound Interest",
            "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "The difference between the CI and SI on a certain sum of money for 3 years at 5% per annum is ₹244. Find the principal.",
            "question_hi": "एक निश्चित राशि पर 3 वर्षों के लिए 5% प्रति वर्ष की दर से CI और SI के बीच का अंतर ₹244 है। मूलधन ज्ञात कीजिए?",
            "options": [{"id":"A","text":"₹24,000"},{"id":"B","text":"₹35,000"},{"id":"C","text":"₹32,000"},{"id":"D","text":"₹28,000"}],
            "correct": "C",
            "solution": "Difference for 3 years = P(R/100)² (3 + R/100).\nFor R = 5% = 1/20: Difference = P(1/400)(61/20) = 61 P / 8000.\n61 P / 8000 = 244 ⇒ P = (244 × 8000) / 61 = 4 × 8000 = ₹32,000.",
            "trick": "P = 244 × 8000 / 61 = 4 × 8000 = ₹32,000."
        }
    ]
}

# Test 08: Speed, Time, Work, Pipes, Trains, Boats & Races (25 Questions)
test_8 = {
    "id": "cgl-mains-mock-08",
    "title": "SSC CGL Mains 2026 - Speed, Time, Work & Motion Mastery (25 Qs)",
    "subtitle": "Time & Work, Pipes & Cisterns, TSD, Trains, Boats & Streams, Circular Tracks & Races",
    "category": "Time & Motion",
    "durationMinutes": 35,
    "marksPerQuestion": 3,
    "negativeMarks": 1,
    "instructions": ["25 Questions covering Time & Work, Pipes, Speed & Distance, Trains, Boats & Races.", "Tier-2 Marking: +3 correct, -1 wrong."],
    "questions": [
        {
            "id": 1, "topic": "Time & Work", "exam": "CDS Maths Paper-4, 19/11/2017",
            "question_en": "30 men can complete a job in 40 days. However, after 24 days some men out of the assigned 30 left the job. The remaining people took another 40 days to complete the job. The number of men who left the job is:",
            "question_hi": "30 आदमी 40 दिनों में एक काम पूरा कर सकते हैं। हालांकि, 24 दिनों के बाद 30 पुरुषों में से कुछ ने काम छोड़ दिया। शेष लोगों को काम पूरा करने में 40 दिन लग गए। काम छोड़ने वाले पुरुषों की संख्या है:",
            "options": [{"id":"A","text":"24"},{"id":"B","text":"18"},{"id":"C","text":"12"},{"id":"D","text":"6"}],
            "correct": "B",
            "solution": "Remaining work after 24 days was for 30 men for (40 - 24) = 16 days.\nWork = 30 × 16 = 480 man-days.\nLet M men be remaining: M × 40 = 480 ⇒ M = 12 men.\nNumber of men who left = 30 - 12 = 18.",
            "trick": "30 × 16 = (30 - x) × 40 ⇒ 12 = 30 - x ⇒ x = 18."
        },
        {
            "id": 2, "topic": "Time & Work", "exam": "SSC CGL Tier-II, 18/11/2020",
            "question_en": "A, B and C can do a work separately in 18, 36 and 54 days, respectively. They started the work together, but B and C left 5 days and 10 days, respectively before the completion of the work. In how many days was the work finished?",
            "question_hi": "A, B और C किसी काम को अलग-अलग क्रमशः 18, 36 और 54 दिन में कर सकते हैं। उन्होंने एक साथ काम करना शुरू किया, लेकिन, B और C ने काम पूरा होने के पहले क्रमशः 5 दिन और 10 दिन पहले काम छोड़ दिया। कितने दिनों में काम पूरा हुआ?",
            "options": [{"id":"A","text":"13 days"},{"id":"B","text":"12 days"},{"id":"C","text":"14 days"},{"id":"D","text":"15 days"}],
            "correct": "A",
            "solution": "Total work = LCM(18, 36, 54) = 108 units.\nEfficiencies: A = 6, B = 3, C = 2 units/day (Total = 11 units/day).\nAdd the work of those who left before completion:\nB's 5 days work = 5 × 3 = 15 units.\nC's 10 days work = 10 × 2 = 20 units.\nAdjusted Total Work = 108 + 15 + 20 = 143 units.\nTotal days = 143 / 11 = 13 days.",
            "trick": "(108 + 15 + 20) / 11 = 143 / 11 = 13 days."
        },
        {
            "id": 3, "topic": "Time & Work", "exam": "SSC CGL Tier-II, 18/01/2025",
            "question_en": "Rani and Adhya, working separately, can finish a task in 12 days and 16 days respectively. They work in stretches of one day alternately. If Rani starts working first, then the task will be completed in:",
            "question_hi": "रानी और अध्या अलग-अलग काम करते हुए एक काम को क्रमशः 12 दिन और 16 दिन में पूरा कर सकती हैं। वे बारी-बारी से एक-एक दिन काम करती हैं। यदि रानी पहले काम करना शुरू करती है, तो काम कितने दिनों में पूरा हो जाएगा?",
            "options": [{"id":"A","text":"12 1/3 days"},{"id":"B","text":"13 2/3 days"},{"id":"C","text":"13 1/3 days"},{"id":"D","text":"12 2/3 days"}],
            "correct": "B",
            "solution": "Total work = LCM(12, 16) = 48 units.\nEfficiencies: Rani = 4, Adhya = 3.\nIn 2 days: Rani + Adhya = 4 + 3 = 7 units.\nIn 6 pairs (12 days): 6 × 7 = 42 units.\nDay 13: Rani does 4 units (Total = 46 units). 2 units remain.\nDay 14: Adhya does 2 units in 2/3 day.\nTotal time = 13 + 2/3 = 13 2/3 days.",
            "trick": "12 days = 42 units, 13th day = 46 units, remaining 2 units by Adhya = 2/3 day ⇒ 13 2/3 days."
        },
        {
            "id": 4, "topic": "Time & Work", "exam": "CDS Paper-2, 23/10/2016",
            "question_en": "A can do 50% more work than B in the same time. B alone can do a piece of work in 30 h. B starts working and had already worked for 12 h when A joins him. How many hours should B and A work together to complete the remaining work?",
            "question_hi": "A, B की तुलना में समान समय में 50% ज़्यादा काम कर सकता है। B अकेले किसी काम को 30 घंटे में पूरा कर सकता है। B काम शुरू करता है और 12 घंटे तक काम करने के बाद A उसके साथ जुड़ जाता है। बचा हुआ काम पूरा करने के लिए B और A को कितने घंटे साथ काम करना होगा?",
            "options": [{"id":"A","text":"6 h"},{"id":"B","text":"12 h"},{"id":"C","text":"4.8 h"},{"id":"D","text":"7.2 h"}],
            "correct": "D",
            "solution": "Efficiency of B = 2, Efficiency of A = 3 (50% more).\nTotal work = 30 × 2 = 60 units.\nWork done by B in 12 h = 12 × 2 = 24 units.\nRemaining work = 60 - 24 = 36 units.\nCombined efficiency of A + B = 3 + 2 = 5 units/hour.\nTime needed = 36 / 5 = 7.2 hours.",
            "trick": "Remaining 18 hrs of B's work completed by (B + A) = 18 × (2/5) = 7.2 hours."
        },
        {
            "id": 5, "topic": "Time & Work", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "The ratio of efficiency of P & Q is 9 : 5. Working together they can complete a certain work in 7 1/2 days. P alone completed 3/7 part of the work and after which Q alone completed the remaining work. The total number of days in which the entire work got completed is:",
            "question_hi": "P और Q की दक्षता का अनुपात 9:5 है। एक साथ काम करते हुए वे एक निश्चित काम को 7 1/2 दिनों में पूरा कर सकते हैं। P अकेले ने काम का 3/7 भाग पूरा किया और उसके बाद Q अकेले ने शेष काम पूरा किया। पूरा काम जिस कुल दिनों में पूरा हुआ, उसकी संख्या क्या है?",
            "options": [{"id":"A","text":"12 days"},{"id":"B","text":"15 days"},{"id":"C","text":"17 days"},{"id":"D","text":"18 days"}],
            "correct": "C",
            "solution": "Efficiency P = 9, Q = 5. Combined = 14.\nTotal work = 14 × 7.5 = 105 units.\nP does 3/7 of work = (3/7) × 105 = 45 units. Time for P = 45 / 9 = 5 days.\nQ does remaining 60 units. Time for Q = 60 / 5 = 12 days.\nTotal days = 5 + 12 = 17 days.",
            "trick": "Time = (45/9) + (60/5) = 5 + 12 = 17 days."
        },
        {
            "id": 6, "topic": "Time & Work", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "A and B can do a work in 35 days and 42 days respectively. They began the work together, but A left after some time and B finished the remaining work in 9 days. After how many days did A leave the work?",
            "question_hi": "A और B एक काम को क्रमशः 35 दिनों और 42 दिनों में कर सकते हैं। उन्होंने एक साथ काम शुरू किया, लेकिन A कुछ समय बाद छोड़ गया और B ने शेष काम 9 दिनों में पूरा किया। A ने कितने दिनों बाद काम छोड़ा?",
            "options": [{"id":"A","text":"14 days"},{"id":"B","text":"13 days"},{"id":"C","text":"12 days"},{"id":"D","text":"15 days"}],
            "correct": "D",
            "solution": "Total work = LCM(35, 42) = 210 units.\nEfficiency A = 6, B = 5.\nWork done by B in last 9 days = 9 × 5 = 45 units.\nRemaining work done by A + B together = 210 - 45 = 165 units.\nCombined efficiency = 6 + 5 = 11 units/day.\nDays worked together = 165 / 11 = 15 days.",
            "trick": "(210 - 45) / 11 = 165 / 11 = 15 days."
        },
        {
            "id": 7, "topic": "Pipe & Cistern", "exam": "SSC CGL Tier-II, 12/09/2019",
            "question_en": "Three pipes A, B and C can fill a cistern in 24, 45 and 36 minutes, respectively. If all the pipes are opened together for 13 minutes, what will be the volume of the water that overflows as the percentage of the total volume of the cistern?",
            "question_hi": "तीन पाइप A, B और C एक टंकी को क्रमशः 24, 36 और 45 मिनट में भर सकते हैं। यदि सभी पाइपों को एक साथ 13 मिनट के लिए खोल दिया जाए, तो टंकी से बाहर बहने वाले पानी का आयतन, टंकी के कुल आयतन का कितना प्रतिशत होगा?",
            "options": [{"id":"A","text":"19.20%"},{"id":"B","text":"19.66%"},{"id":"C","text":"18.33%"},{"id":"D","text":"20.75%"}],
            "correct": "A",
            "solution": "Total capacity = LCM(24, 45, 36) = 360 units.\nEfficiencies: A = 15, B = 8, C = 10 units/min.\nCombined rate = 15 + 8 + 10 = 33 units/min.\nIn 13 minutes: 33 × 13 = 429 units filled.\nOverflow = 429 - 360 = 69 units.\nPercentage overflow = (69 / 360) × 100% = 19.16% ≈ 19.20%.",
            "trick": "Overflow% = (429 - 360)/360 × 100% = 69/360 × 100% ≈ 19.20%."
        },
        {
            "id": 8, "topic": "Pipe & Cistern", "exam": "SSC CGL Tier-II, 03/03/2023",
            "question_en": "Two inlets A and B are connected to a tank and can fill it in 32 h and 28 h respectively. If both the pipes are opened alternately for 1 h, starting from A, then in how much time (in hours to the nearest round) the tank will be filled?",
            "question_hi": "एक टैंक से दो इनलेट A और B जुड़े हुए है। A और B टैंक को क्रमशः 32 घंटे और 28 घंटे में भर सकते है। यदि दोनों पाईपो को A से शुरू करते हुए, बारी-बारी से, 1 घंटा के लिए खोला जाता है, तो टैंक कितने समय (घंटो में निकटतम पूर्णांक) में भर जायेगा?",
            "options": [{"id":"A","text":"36 h"},{"id":"B","text":"22 h"},{"id":"C","text":"24 h"},{"id":"D","text":"30 h"}],
            "correct": "D",
            "solution": "Total capacity = LCM(32, 28) = 224 units.\nEfficiency A = 7, B = 8 units/hour.\nIn 2 hours: A + B = 7 + 8 = 15 units.\nIn 14 pairs (28 hours): 14 × 15 = 210 units.\nRemaining = 224 - 210 = 14 units.\nHour 29 (Pipe A): fills 7 units (Total = 217 units).\nHour 30 (Pipe B): remaining 7 units filled in 7/8 hour.\nTotal time = 29 7/8 hours ≈ 30 hours.",
            "trick": "224 / 7.5 ≈ 29.87 hours ≈ 30 hours."
        },
        {
            "id": 9, "topic": "Pipe & Cistern", "exam": "SSC CGL Tier-II, 02/03/2023",
            "question_en": "There are three taps of diameter 2 cm, 3 cm and 4 cm respectively. The ratio of the water flowing through them is equal to the ratio of the square of their diameters. The largest tap alone can fill an empty tank in 81 minutes. If all the taps are opened simultaneously, then how much time (in minutes) will it take to fill the tank?",
            "question_hi": "क्रमशः 2 cm, 3 cm और 4 cm व्यास के तीन नल है। उनके माध्यम से प्रवाहित जल का अनुपात उनके व्यास के वर्ग के अनुपात के बराबर है। सबसे बड़ा नल अकेले एक खाली टंकी को 81 मिनट में भर सकता है। यदि सभी नलो को एक साथ खोल दिया जाये, तो टंकी को भरने में कितना समय (मिनट में) लगेगा?",
            "options": [{"id":"A","text":"34 20/29 min"},{"id":"B","text":"54 20/29 min"},{"id":"C","text":"64 20/29 min"},{"id":"D","text":"44 20/29 min"}],
            "correct": "D",
            "solution": "Flow rate ratio = 2² : 3² : 4² = 4 : 9 : 16.\nLargest tap rate = 16 units/min.\nTotal capacity = 16 × 81 = 1296 units.\nCombined rate of all three taps = 4 + 9 + 16 = 29 units/min.\nTime = 1296 / 29 = 44 20/29 minutes.",
            "trick": "Time = (16 × 81) / 29 = 1296 / 29 = 44 20/29 minutes."
        },
        {
            "id": 10, "topic": "Pipe & Cistern", "exam": "IB Security Assistant / Executive 2025",
            "question_en": "A reservoir has three pipes P, Q, and R. When pipes P and Q are opened together, they can fill the empty reservoir in 12 hours. When pipes Q and R are opened together, it can be filled in 16 hours. If pipe P can fill the reservoir three times as fast as pipe R, how long will it take for all three pipes working together to fill the empty reservoir?",
            "question_hi": "एक जलाशय में तीन पाइप P, Q और R हैं। जब पाइप P और Q को एक साथ खोला जाता है, तो वे खाली जलाशय को 12 घंटे में भर सकते हैं। जब पाइप Q और R को एक साथ खोला जाता है, तो वे खाली जलाशय को 16 घंटे में भर सकते है। यदि पाइप P, पाइप R की तुलना में तीन गुना तेजी से जलाशय को भर सकता है, तो तीनों पाइपों को एक साथ चालू करने पर कितना समय लगेगा?",
            "options": [{"id":"A","text":"9 hours 30 min"},{"id":"B","text":"12 hours 20 min"},{"id":"C","text":"10 hours 40 min"},{"id":"D","text":"8 hours 10 min"}],
            "correct": "C",
            "solution": "Total work = LCM(12, 16) = 48 units.\nP + Q = 4 units/hr, Q + R = 3 units/hr.\nSubtracting: P - R = 4 - 3 = 1 unit/hr.\nGiven P = 3R ⇒ 3R - R = 1 ⇒ 2R = 1 ⇒ R = 0.5 unit/hr.\nP = 1.5 units/hr.\nQ = 4 - 1.5 = 2.5 units/hr.\nP + Q + R = 1.5 + 2.5 + 0.5 = 4.5 units/hr.\nTime = 48 / 4.5 = 48 / (9/2) = 96 / 9 = 32 / 3 hours = 10 hours 40 minutes.",
            "trick": "48 / 4.5 = 10 2/3 hrs = 10 hours 40 minutes."
        },
        {
            "id": 11, "topic": "Time, Speed & Distance", "exam": "SSC CHSL Tier-II, 02/11/2023",
            "question_en": "A person covers 1/4 of his journey at the speed of 25 km/h, 1/2 of the journey at 40 km/h and the remaining at 50 km/h. Find his average speed per hour for the whole journey (in km/h).",
            "question_hi": "एक व्यक्ति अपनी यात्रा का 1/4 भाग 25 किमी/घंटा की चाल से, 1/2 यात्रा का भाग 40 किमी/घंटा की चाल से और यात्रा का शेष भाग 50 किमी/घंटा की चाल से तय करता है। पूरी यात्रा के दौरान उसकी प्रति घंटा औसत चाल (किमी/घंटा में) ज्ञात कीजिए।",
            "options": [{"id":"A","text":"37 6/11"},{"id":"B","text":"36 4/11"},{"id":"C","text":"36 6/11"},{"id":"D","text":"34 4/11"}],
            "correct": "B",
            "solution": "Let total distance = 400 km.\n1/4 distance = 100 km at 25 km/h ⇒ Time = 4 hours.\n1/2 distance = 200 km at 40 km/h ⇒ Time = 5 hours.\nRemaining 1/4 distance = 100 km at 50 km/h ⇒ Time = 2 hours.\nTotal Time = 4 + 5 + 2 = 11 hours.\nAverage speed = 400 / 11 = 36 4/11 km/h.",
            "trick": "400 / (4 + 5 + 2) = 400 / 11 = 36 4/11 km/h."
        },
        {
            "id": 12, "topic": "Time, Speed & Distance", "exam": "CDS Elementary, 21/04/2024",
            "question_en": "Two trains A and B leave Delhi for Hyderabad at 7:00 am and 7:50 am on the same day and travel at 80 km/h and 100 km/h respectively. After how many kilometers from Delhi will the two trains be together?",
            "question_hi": "दो ट्रेनें A और B एक ही दिन सुबह 7:00 बजे और 7:50 बजे दिल्ली से हैदराबाद के लिए रवाना होती हैं और क्रमशः 80 किमी/घंटा और 100 किमी/घंटा की गति से यात्रा करती हैं। दिल्ली से कितने किलोमीटर बाद दोनों ट्रेनें एक साथ होंगी?",
            "options": [{"id":"A","text":"200/3 km"},{"id":"B","text":"100 km"},{"id":"C","text":"400/3 km"},{"id":"D","text":"1000/3 km"}],
            "correct": "D",
            "solution": "Train A runs alone for 50 minutes = 50/60 = 5/6 hour.\nDistance covered by A in 50 min = 80 × 5/6 = 200/3 km.\nRelative speed = 100 - 80 = 20 km/h.\nTime to catch up = (200/3) / 20 = 10/3 hours.\nDistance from Delhi = Speed of B × Time = 100 × (10/3) = 1000/3 km.",
            "trick": "D = (80 × 100 × 50/60) / (100 - 80) = (8000 × 5/6) / 20 = 1000/3 km."
        },
        {
            "id": 13, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "Two stations X and Y are 900 km apart. Train P starts from station X and travels toward Y and at the same time train Q starts from station Y and travels toward X. Train Q is 50% faster than train P and both trains travel at constant speeds. Find the distance from station Y to the point where the two trains meet.",
            "question_hi": "दो स्टेशन X और Y 900 km दूर हैं। ट्रेन P स्टेशन X से Y की ओर चलना शुरू करती है और उसी समय ट्रेन Q स्टेशन Y से X की ओर चलना शुरू करती है। ट्रेन Q, ट्रेन P से 50% तेज है। उस बिंदु से स्टेशन Y की दूरी ज्ञात कीजिए जहाँ दोनों ट्रेनें मिलती हैं?",
            "options": [{"id":"A","text":"360 km"},{"id":"B","text":"540 km"},{"id":"C","text":"180 km"},{"id":"D","text":"420 km"}],
            "correct": "B",
            "solution": "Speed ratio P : Q = 100 : 150 = 2 : 3.\nSince time is same, distance covered is in ratio 2 : 3.\nTotal distance = 5 units = 900 km ⇒ 1 unit = 180 km.\nDistance from station Y = Distance covered by Q = 3 units = 3 × 180 = 540 km.",
            "trick": "900 × 3/5 = 540 km."
        },
        {
            "id": 14, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "A man begins his trip 36 minutes later than his regular starting time. To make up for the delay, he travels at 180% of his usual speed and ends up reaching his destination 16 minutes earlier than his usual arrival time. Find the usual time taken for the journey.",
            "question_hi": "एक आदमी अपनी यात्रा नियमित शुरुआती समय से 36 मिनट देरी से शुरू करता है। देरी की भरपाई के लिए, वह अपनी सामान्य गति के 180% पर यात्रा करता है और अपने गंतव्य पर नियमित आगमन समय से 16 मिनट पहले पहुँच जाता है। यात्रा के लिए सामान्य समय ज्ञात कीजिए?",
            "options": [{"id":"A","text":"95 minutes"},{"id":"B","text":"117 minutes"},{"id":"C","text":"104 minutes"},{"id":"D","text":"119 minutes"}],
            "correct": "B",
            "solution": "Speed ratio = 100 : 180 = 5 : 9.\nTime ratio = 9 : 5.\nDifference in time ratio = 9 - 5 = 4 units.\nActual time saved = 36 min delay + 16 min early = 52 minutes.\n4 units = 52 minutes ⇒ 1 unit = 13 minutes.\nUsual time = 9 units = 9 × 13 = 117 minutes.",
            "trick": "Usual time = (52 / 4) × 9 = 117 minutes."
        },
        {
            "id": 15, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "A train going from P to Q meets an accident after travelling 90 km. Due to the accident, the train reduces its speed to 2/3 of its normal speed and reaches its destination 30 minutes late. Had the same accident occurred 60 km further, the train would have reached just 10 min late. What is the distance from P to Q?",
            "question_hi": "एक ट्रेन P से Q जाते हुए, 90 km चलने के बाद एक दुर्घटना का सामना करती है। दुर्घटना के कारण, ट्रेन अपनी सामान्य गति को 2/3 कर देती है और 30 मिनट देरी से पहुँचती है, यदि वही दुर्घटना 60 km आगे हुई होती तो ट्रेन केवल 10 मिनट देरी से पहुँचती। P से Q की दूरी क्या है?",
            "options": [{"id":"A","text":"170 km"},{"id":"B","text":"180 km"},{"id":"C","text":"210 km"},{"id":"D","text":"190 km"}],
            "correct": "B",
            "solution": "In 60 km, delay reduces by (30 - 10) = 20 minutes.\nRate of delay = 20 min / 60 km = 1 min / 3 km.\nTo save full 30 minutes of delay, distance remaining after first accident = 30 × 3 = 90 km.\nTotal distance = 90 km (before accident) + 90 km (after accident) = 180 km.",
            "trick": "Delay of 20 min in 60 km ⇒ 1 min in 3 km. For 30 min delay, distance = 90 km. Total = 90 + 90 = 180 km."
        },
        {
            "id": 16, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE HIGHER SECONDARY 2026",
            "question_en": "A car travels from city P to city Q at a constant speed. If its speed were increased by 6 km/h, the trip would take 1 hour less. If the speed were further increased by 4 km/h (i.e. 10 km/h more than original), the trip would take an additional 30 minutes less. What is the distance between the two cities?",
            "question_hi": "एक कार शहर P से शहर Q तक निरंतर गति से यात्रा करती है। यदि इसकी गति 6 km/h बढ़ा दी जाती है, तो यात्रा 1 घंटा कम समय लेती है। यदि गति को और 4 km/h बढ़ा दिया जाता है (यानी मूल से 10 km/h अधिक), तो यात्रा अतिरिक्त 30 मिनट कम समय लेती है। दोनों शहरों के बीच की दूरी क्या है?",
            "options": [{"id":"A","text":"360 km"},{"id":"B","text":"180 km"},{"id":"C","text":"40 km"},{"id":"D","text":"200 km"}],
            "correct": "B",
            "solution": "Distance formula: D = [S(S + 6)/6] × 1 = [S(S + 10)/10] × 1.5\n⇒ (S + 6)/6 = 1.5(S + 10)/10 = 3(S + 10)/20\n⇒ 20(S + 6) = 18(S + 10) ⇒ 20S + 120 = 18S + 180 ⇒ 2S = 60 ⇒ S = 30 km/h.\nD = [30 × 36 / 6] × 1 = 180 km.",
            "trick": "S = 30 km/h ⇒ D = (30 × 36) / 6 = 180 km."
        },
        {
            "id": 17, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE MATRIC LEVEL 2026",
            "question_en": "A boat travels 36 km downstream in 3 hours and the same distance upstream in 4.5 hours. What is the speed of the boat in still water?",
            "question_hi": "एक नाव धारा के अनुकूल 36 km की दूरी 3 घंटे में तय करती है और इतनी ही दूरी धारा के प्रतिकूल 4.5 घंटे में तय करती है। स्थिर जल में नाव की चाल क्या है?",
            "options": [{"id":"A","text":"8 km/h"},{"id":"B","text":"9 km/h"},{"id":"C","text":"10 km/h"},{"id":"D","text":"12 km/h"}],
            "correct": "C",
            "solution": "Downstream speed D = 36 / 3 = 12 km/h.\nUpstream speed U = 36 / 4.5 = 8 km/h.\nSpeed in still water = (D + U) / 2 = (12 + 8) / 2 = 10 km/h.",
            "trick": "(12 + 8) / 2 = 10 km/h."
        },
        {
            "id": 18, "topic": "Time, Speed & Distance", "exam": "SSC SELECTION PHASE MATRIC LEVEL 2026",
            "question_en": "Amit travels from A to B at 60 km/hr and returns from B to A at a different speed. His overall average speed is 48 km/hr. What was his speed from B to A?",
            "question_hi": "अमित A से B तक 60 km/hr की गति से जाता है और B से A तक भिन्न गति से वापस लौटता है। उसकी कुल औसत गति 48 km/hr है। B से A तक उसकी गति क्या थी?",
            "options": [{"id":"A","text":"42 km/hr"},{"id":"B","text":"38 km/hr"},{"id":"C","text":"32 km/hr"},{"id":"D","text":"40 km/hr"}],
            "correct": "D",
            "solution": "Average speed = 2xy / (x + y)\n48 = (2 × 60 × y) / (60 + y) = 120y / (60 + y)\n⇒ 48(60 + y) = 120y ⇒ 2880 + 48y = 120y ⇒ 72y = 2880 ⇒ y = 40 km/hr.",
            "trick": "48 = 120y / (60 + y) ⇒ y = 40 km/hr."
        },
        {
            "id": 19, "topic": "Train", "exam": "SSC CGL Tier-II, 07/03/2023",
            "question_en": "Two trains, A and B, of lengths 180 m and 220 m, respectively, are running on parallel tracks in opposite directions. They cross each other in 12 seconds. If the same two trains are moving in the same direction, they take 60 seconds for the faster train to completely cross the slower one. Find the speed (in km/h) of the faster train.",
            "question_hi": "दो ट्रेनें, A और B, जिनकी लंबाई क्रमशः 180 मी. और 220 मी. है, समानांतर पटरियों पर विपरीत दिशाओं में चल रही हैं। वे 12 सेकंड में एक-दूसरे को पार कर लेती हैं। यदि वही दोनों ट्रेनें एक ही दिशा में चलती हैं, तो तेज चाल वाली ट्रेन द्वारा धीमी चाल वाली ट्रेन को पूर्ण रूप से पार करने में 60 सेकंड लगते हैं। तेज चाल वाली ट्रेन की चाल (किमी/घंटा में) ज्ञात कीजिए:",
            "options": [{"id":"A","text":"72 km/h"},{"id":"B","text":"80 km/h"},{"id":"C","text":"64 km/h"},{"id":"D","text":"48 km/h"}],
            "correct": "A",
            "solution": "Total length = 180 + 220 = 400 m.\nOpposite direction (S1 + S2) = 400 / 12 = 100/3 m/s.\nSame direction (S1 - S2) = 400 / 60 = 20/3 m/s.\nAdding both equations: 2 S1 = 120/3 = 40 ⇒ S1 = 20 m/s.\nSpeed in km/h = 20 × (18/5) = 72 km/h.",
            "trick": "S1 = (400/12 + 400/60) / 2 = (100/3 + 20/3) / 2 = 20 m/s = 72 km/h."
        },
        {
            "id": 20, "topic": "Train", "exam": "SSC CHSL Tier-I, 17/11/2025",
            "question_en": "Train ‘P’ can cross a pole in 8 seconds, while train ‘Q’ takes 15 seconds to cross train ‘P’ when they travel in opposite directions on parallel tracks. If the ratio of length of train ‘P’ to that of train ‘Q’ is 2 : 3 and the speed of train ‘P’ is 54 km/h, then find the speed (in km/h) of train ‘Q’.",
            "question_hi": "रेलगाड़ी ‘P’ एक खंभे को 8 सेकंड में पार कर सकती है, जबकि रेलगाड़ी ‘Q’ को रेलगाड़ी ‘P’ को पार करने में 15 सेकंड लगते हैं, जब वे समानांतर पटरियों पर विपरीत दिशाओं में चलती हैं। यदि रेलगाड़ी ‘P’ और रेलगाड़ी ‘Q’ की लंबाई का अनुपात 2 : 3 है तथा रेलगाड़ी ‘P’ की चाल 54 किमी/घंटा है, तो रेलगाड़ी ‘Q’ की चाल (किमी/घंटा में) ज्ञात कीजिए।",
            "options": [{"id":"A","text":"28 km/h"},{"id":"B","text":"12 km/h"},{"id":"C","text":"22 km/h"},{"id":"D","text":"18 km/h"}],
            "correct": "D",
            "solution": "Speed of P = 54 × (5/18) = 15 m/s.\nLength of P = 15 × 8 = 120 m.\nLength of Q = (3/2) × 120 = 180 m.\nTotal distance = 120 + 180 = 300 m.\nRelative speed = 300 / 15 = 20 m/s.\nSpeed of Q = 20 - 15 = 5 m/s = 5 × (18/5) = 18 km/h.",
            "trick": "Sp + Sq = 300/15 = 20 m/s. Sq = 20 - 15 = 5 m/s = 18 km/h."
        },
        {
            "id": 21, "topic": "Train", "exam": "SSC CHSL Tier-I, 26/11/2025",
            "question_en": "Train A running at a speed of 72 km/hr takes 24 seconds to completely cross train B running at 63 km/hr in the opposite direction. The length of train B is 1.5 times the length of train A. Train B crosses a bridge completely in 62 seconds. The length of the bridge (in m) is:",
            "question_hi": "72 किमी./घंटा की चाल से चलने वाली ट्रेन A को विपरीत दिशा में 63 किमी./घंटा की चाल से चलने वाली ट्रेन B को पूरी तरह से पार करने में 24 सेकंड लगते हैं। ट्रेन B की लंबाई ट्रेन A की लंबाई की 1.5 गुनी है। ट्रेन B पुल को 62 सेकंड में पूरी तरह से पार करती है। पुल की लंबाई (मीटर में) कितनी है?",
            "options": [{"id":"A","text":"626 m"},{"id":"B","text":"445 m"},{"id":"C","text":"433 m"},{"id":"D","text":"545 m"}],
            "correct": "D",
            "solution": "Relative speed = (72 + 63) × (5/18) = 135 × (5/18) = 37.5 m/s.\nTotal distance = 37.5 × 24 = 900 m.\nLa + Lb = 900 m. Since Lb = 1.5 La ⇒ 2.5 La = 900 ⇒ La = 360 m, Lb = 540 m.\nSpeed of B = 63 × (5/18) = 17.5 m/s.\nDistance in 62 s = 17.5 × 62 = 1085 m.\nBridge length = 1085 - 540 = 545 m.",
            "trick": "Lb = 540 m. Bridge = 17.5 × 62 - 540 = 1085 - 540 = 545 m."
        },
        {
            "id": 22, "topic": "Boat & Stream",
            "exam": "IB ACIO GRADE-2 2025",
            "question_en": "A man can row 30 km upstream and 55 km downstream in the same amount of time as he can row 38.5 km downstream and 37.5 km upstream. Find the ratio of the rowing speed to the speed of the current.",
            "question_hi": "एक व्यक्ति धारा की विपरीत दिशा में 30 km और धारा की दिशा में 55 km उतने ही समय में नाव चला सकता है जितने समय में वह धारा की दिशा में 38.5 km और धारा की विपरीत दिशा में 37.5 km नाव चला सकता है। नाव की चाल और धारा की चाल का अनुपात ज्ञात कीजिए।",
            "options": [{"id":"A","text":"9 : 2"},{"id":"B","text":"7 : 2"},{"id":"C","text":"5 : 3"},{"id":"D","text":"8 : 3"}],
            "correct": "D",
            "solution": "30/U + 55/D = 37.5/U + 38.5/D\n⇒ (55 - 38.5)/D = (37.5 - 30)/U\n⇒ 16.5 / D = 7.5 / U ⇒ D / U = 16.5 / 7.5 = 11 / 5.\nRowing speed : Current speed = (D + U) : (D - U) = (11 + 5) : (11 - 5) = 16 : 6 = 8 : 3.",
            "trick": "(11 + 5) : (11 - 5) = 16 : 6 = 8 : 3."
        },
        {
            "id": 23, "topic": "Race",
            "exam": "SSC CHSL Tier-II, 18/11/2024",
            "question_en": "In a 2400 m race, Tarun gives an initial lead of 60 seconds to Hari and still beats him by 40 seconds. If the speed of Hari is 6 m/sec, then find the speed of Tarun.",
            "question_hi": "2400 मीटर की दौड़ में तरुण, हरी को 60 सेकंड की शुरुआती बढ़त देता और फिर भी उसे 40 सेकंड से हरा देता है। यदि हरी की चाल 6 मीटर/सेकंड है, तो तरुण की चाल ज्ञात कीजिये?",
            "options": [{"id":"A","text":"8.5 m/s"},{"id":"B","text":"7 m/s"},{"id":"C","text":"7.5 m/s"},{"id":"D","text":"8 m/s"}],
            "correct": "D",
            "solution": "Hari's time for 2400 m = 2400 / 6 = 400 seconds.\nTarun gives 60s lead and beats by 40s ⇒ Tarun ran for: 400 - 60 - 40 = 300 seconds.\nSpeed of Tarun = 2400 / 300 = 8 m/s.",
            "trick": "2400 / (400 - 100) = 2400 / 300 = 8 m/s."
        },
        {
            "id": 24, "topic": "Race",
            "exam": "IB ACIO GRADE-2 2025",
            "question_en": "Around a circular track, A and B walk in opposite directions at speeds of 5 rounds per hour and 6 rounds per hour, respectively. How many times will they cross each other in 2.5 hours?",
            "question_hi": "एक वृत्ताकार पथ पर, A और B क्रमशः 5 चक्कर प्रति घंटा और 6 चक्कर प्रति घंटा की चाल से विपरीत दिशा में चलते हैं। 2.5 घंटे में वे एक-दूसरे को कितनी बार पार करेंगे?",
            "options": [{"id":"A","text":"23"},{"id":"B","text":"27"},{"id":"C","text":"25"},{"id":"D","text":"30"}],
            "correct": "B",
            "solution": "Relative speed in opposite directions = 5 + 6 = 11 rounds/hour.\nNumber of crossings in 2.5 hours = 11 × 2.5 = 27.5 ⇒ 27 full crossings.",
            "trick": "Floor(11 × 2.5) = 27."
        },
        {
            "id": 25, "topic": "Race",
            "exam": "SSC CGL Tier-1, 14/09/2025",
            "question_en": "Three friends, X, Y, and Z, are cycling on a circular track with a circumference of 2 km. They all start from the same point at 9:00 a.m. and travel in the same direction with speeds of 10 km/h, 12 km/h, and 15 km/h respectively. How many times will all three of them meet at the starting point if they continue cycling until 1:00 p.m.?",
            "question_hi": "तीन दोस्त, X, Y और Z, 2 किमी परिधि वाले एक वृत्ताकार ट्रैक पर साइकिल चला रहे हैं। वे सभी सुबह 9:00 बजे एक ही बिंदु से चलना शुरू करते हैं और क्रमशः 10 किमी/घंटा, 12 किमी/घंटा और 15 किमी/घंटा की गति से एक ही दिशा में यात्रा करते हैं। यदि वे दोपहर 1:00 बजे तक साइकिल चलाना जारी रखते हैं, तो वे तीनों कितनी बार शुरुआती बिंदु पर मिलेंगे?",
            "options": [{"id":"A","text":"1 time"},{"id":"B","text":"2 times"},{"id":"C","text":"3 times"},{"id":"D","text":"4 times"}],
            "correct": "B",
            "solution": "Time taken by each to complete one round of 2 km:\nt_X = 2 / 10 = 1/5 h = 12 minutes.\nt_Y = 2 / 12 = 1/6 h = 10 minutes.\nt_Z = 2 / 15 h = 8 minutes.\nAll meet at starting point after LCM(12, 10, 8) = 120 minutes = 2 hours.\nFrom 9:00 am to 1:00 pm is 4 hours.\nNumber of meetings at start point = 4 / 2 = 2 times (at 11:00 am and 1:00 pm).",
            "trick": "LCM(12, 10, 8) = 120 min = 2 hrs. In 4 hrs ⇒ 4/2 = 2 times."
        }
    ]
}

with open(os.path.join(tests_dir, "cgl-mains-mock-07.json"), "w", encoding="utf-8") as f:
    json.dump(test_7, f, indent=2, ensure_ascii=False)

with open(os.path.join(tests_dir, "cgl-mains-mock-08.json"), "w", encoding="utf-8") as f:
    json.dump(test_8, f, indent=2, ensure_ascii=False)

print("Generated test-07 and test-08 successfully!")

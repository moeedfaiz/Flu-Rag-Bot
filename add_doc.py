import json, textwrap, os

docs = []

def add_doc(id, category, title, tags, text):
    docs.append({
        "id": id,
        "category": category,
        "title": title,
        "tags": tags,
        "text": textwrap.dedent(text).strip()
    })

# Flu basics
add_doc(
    "doc-001",
    "flu_basics",
    "What is seasonal influenza (flu)?",
    ["flu", "overview", "respiratory infection"],
    """
    Seasonal influenza, commonly called the flu, is an acute respiratory infection caused mainly by influenza A and B viruses.
    It affects the nose, throat and sometimes the lungs. Illness can range from mild to severe, and in high-risk people it can
    lead to complications such as pneumonia and hospitalisation.
    """
)

add_doc(
    "doc-002",
    "flu_basics",
    "How the flu spreads between people",
    ["flu", "transmission", "droplets"],
    """
    Flu spreads primarily through tiny droplets that are released when an infected person coughs, sneezes or talks.
    These droplets can be inhaled by people nearby or land on surfaces such as doorknobs or phones. If someone touches
    a contaminated surface and then touches their eyes, nose or mouth, the virus can enter the body and cause infection.
    """
)

add_doc(
    "doc-003",
    "flu_basics",
    "Incubation and contagious period of flu",
    ["flu", "incubation", "contagious"],
    """
    After exposure to influenza virus, symptoms usually start within one to four days.
    People can be contagious one day before symptoms begin and up to about five to seven days after they start.
    Young children and people with weakened immune systems may spread the virus for an even longer time.
    """
)

# Flu symptoms
add_doc(
    "doc-010",
    "flu_symptoms",
    "Typical flu symptoms in adults",
    ["flu", "symptoms", "adults"],
    """
    Typical flu symptoms in adults include sudden onset of fever or feeling feverish with chills, a dry cough,
    sore throat, runny or stuffy nose, muscle or body aches, headaches and marked tiredness.
    These symptoms often come on quickly over the course of a day rather than building slowly.
    """
)

add_doc(
    "doc-011",
    "flu_symptoms",
    "Gastrointestinal symptoms and flu",
    ["flu", "symptoms", "gastrointestinal"],
    """
    Some people, especially children, may have nausea, vomiting or diarrhoea during a flu illness.
    These gastrointestinal symptoms are usually accompanied by typical respiratory signs such as fever and cough,
    not occurring in isolation.
    """
)

add_doc(
    "doc-012",
    "flu_symptoms",
    "Duration of uncomplicated flu illness",
    ["flu", "course", "duration"],
    """
    In most healthy people, uncomplicated flu improves within a few days to less than two weeks.
    However, the cough and feelings of fatigue can linger longer even after the fever has resolved.
    If symptoms persist or suddenly worsen, it may indicate a complication such as pneumonia.
    """
)

add_doc(
    "doc-013",
    "flu_symptoms",
    "Children and flu symptoms",
    ["flu", "children", "symptoms"],
    """
    Children with the flu often show many of the same symptoms as adults, including fever, cough, sore throat and tiredness.
    They may also be more likely to have ear pain, vomiting or diarrhoea. Very young children can simply appear irritable,
    feed poorly or be less active than usual.
    """
)

add_doc(
    "doc-014",
    "flu_symptoms",
    "Mild versus severe flu presentations",
    ["flu", "mild", "severe"],
    """
    Some flu illnesses are mild, with low fever and a few respiratory symptoms, while others are more intense and exhausting.
    Even when symptoms are mild, people with underlying chronic conditions or who are pregnant can be at higher risk of complications
    and should consider early medical advice.
    """
)

# Differential: flu vs cold vs allergy
add_doc(
    "doc-020",
    "comparison",
    "Flu versus common cold",
    ["flu", "cold", "difference"],
    """
    Both flu and the common cold can cause cough, sore throat and runny nose, but there are important differences.
    Flu usually starts suddenly and tends to cause higher fever, stronger body aches and more pronounced fatigue.
    Colds often develop gradually and symptoms are milder, with people usually well enough to continue daily activities.
    """
)

add_doc(
    "doc-021",
    "comparison",
    "Flu versus seasonal allergies",
    ["flu", "allergy", "difference"],
    """
    Seasonal allergies are caused by the immune system reacting to things like pollen, not by a virus.
    Allergies commonly cause itchy eyes, itchy nose, sneezing and clear runny nose, but they do not usually cause fever or body aches.
    In contrast, flu commonly causes fever, muscle aches and general sickness, and eye itching is less typical.
    """
)

add_doc(
    "doc-022",
    "comparison",
    "When flu symptoms overlap with other illnesses",
    ["flu", "overlap", "respiratory"],
    """
    Flu symptoms overlap with many other respiratory illnesses, including other viral infections.
    Having fever and cough does not guarantee that a person has influenza specifically.
    Laboratory tests or clinical evaluation by a healthcare professional are often needed to confirm the exact cause.
    """
)

add_doc(
    "doc-023",
    "comparison",
    "No single symptom proves flu",
    ["flu", "diagnosis", "symptoms"],
    """
    No single symptom, such as fever or cough, can by itself prove that someone has the flu.
    Clinicians look at the full pattern of symptoms, the time of year, local flu activity and sometimes test results.
    A simple screening tool or chatbot can only estimate similarity, not make a real diagnosis.
    """
)

add_doc(
    "doc-024",
    "comparison",
    "Muscle aches and fatigue in flu",
    ["flu", "muscle aches", "fatigue"],
    """
    Muscle or body aches and strong fatigue are very common in flu and often make people feel too exhausted to continue normal tasks.
    These symptoms can also appear with other viral infections or with non-infectious problems such as over-exertion or poor sleep.
    Considering other symptoms like fever and cough helps put them in context.
    """
)

# High-risk groups
add_doc(
    "doc-030",
    "risk_groups",
    "People at higher risk of severe flu",
    ["flu", "risk groups", "complications"],
    """
    Some people are at higher risk of severe illness from flu. These include adults 65 years and older, children under five years,
    pregnant people, residents of long-term care facilities and individuals with chronic conditions such as heart disease, lung disease,
    diabetes or weakened immune systems.
    """
)

add_doc(
    "doc-031",
    "risk_groups",
    "Why high-risk groups matter for flu",
    ["flu", "risk", "high risk"],
    """
    In high-risk groups, flu can more easily lead to complications like pneumonia, worsening of chronic illness or hospitalisation.
    For this reason, early medical assessment and, in some cases, antiviral treatment may be recommended when they develop flu-like symptoms.
    """
)

add_doc(
    "doc-032",
    "risk_groups",
    "Flu and pregnancy",
    ["flu", "pregnancy", "risk"],
    """
    Pregnant people have changes in the heart, lungs and immune system that can make flu more serious.
    Vaccination against flu is often recommended in pregnancy, and pregnant individuals with flu-like symptoms are generally advised
    to contact a healthcare professional promptly for guidance.
    """
)

# Red flags and emergency signs
add_doc(
    "doc-040",
    "red_flags",
    "Warning signs in adults with flu-like illness",
    ["flu", "red flags", "adults"],
    """
    Adults with flu-like illness should seek urgent medical care if they develop difficulty breathing or shortness of breath,
    pain or pressure in the chest, sudden confusion, severe or persistent vomiting, or signs of low oxygen such as bluish lips or face.
    Worsening symptoms after initially feeling better can also be a warning sign.
    """
)

add_doc(
    "doc-041",
    "red_flags",
    "Warning signs in children with flu-like illness",
    ["flu", "red flags", "children"],
    """
    In children, warning signs include fast or troubled breathing, bluish skin, not drinking enough fluids,
    not waking up or not interacting, extreme irritability, fever with rash or seizures.
    Any very young infant with fever should be assessed by a healthcare professional urgently.
    """
)

add_doc(
    "doc-042",
    "red_flags",
    "When to seek emergency care for respiratory illness",
    ["flu", "emergency", "respiratory"],
    """
    Regardless of the cause, chest pain, severe breathing difficulty, sudden confusion or inability to stay awake
    are reasons to seek emergency care. These signs can appear with flu or other serious conditions
    and should not be managed at home without medical evaluation.
    """
)

# Prevention and vaccination
add_doc(
    "doc-050",
    "prevention",
    "Flu vaccination as prevention",
    ["flu", "vaccine", "prevention"],
    """
    Yearly flu vaccination is one of the most effective ways to reduce the risk of getting influenza and its complications.
    Vaccines are updated regularly to match circulating strains as closely as possible. Even when vaccination does not fully prevent infection,
    it often makes illness milder and less likely to lead to hospitalisation.
    """
)

add_doc(
    "doc-051",
    "prevention",
    "Everyday actions to reduce flu spread",
    ["flu", "prevention", "hygiene"],
    """
    Basic hygiene measures can help reduce the spread of flu. These include washing hands frequently with soap and water or using alcohol-based hand rub,
    covering coughs and sneezes with a tissue or elbow, avoiding close contact with people who are sick, improving ventilation and staying home when ill.
    """
)

add_doc(
    "doc-052",
    "prevention",
    "Staying home when sick with flu-like illness",
    ["flu", "isolation", "prevention"],
    """
    People with flu-like symptoms should stay home from work, school and social events until at least 24 hours after their fever has gone
    without the use of fever-reducing medicine. This helps protect others, especially those who are at higher risk of severe disease.
    """
)

add_doc(
    "doc-053",
    "prevention",
    "Masks and flu transmission",
    ["flu", "masks", "prevention"],
    """
    Wearing a well-fitting mask can reduce the spread of respiratory droplets that may contain flu virus,
    particularly in crowded indoor settings or when someone has symptoms. Mask use is especially useful
    when flu activity in the community is high or when close contact with high-risk individuals cannot be avoided.
    """
)

# Self-care and basic management
add_doc(
    "doc-060",
    "self_care",
    "Home care for mild flu",
    ["flu", "self care", "home"],
    """
    Mild flu can often be managed at home with rest, plenty of fluids, and over-the-counter medicines for fever and pain,
    following local guidance and package instructions. People should avoid smoking and alcohol, which can irritate the airways and slow recovery.
    """
)

add_doc(
    "doc-061",
    "self_care",
    "Monitoring symptoms at home",
    ["flu", "self care", "monitoring"],
    """
    When caring for flu at home, it is helpful to monitor temperature, breathing and how the person is feeling overall.
    If fever persists for many days, breathing becomes difficult, or confusion or chest pain develops, medical attention should be sought.
    """
)

add_doc(
    "doc-062",
    "self_care",
    "Role of antiviral medicines for flu",
    ["flu", "antiviral", "treatment"],
    """
    In some situations, doctors may prescribe antiviral medicines for flu.
    These medicines work best when started soon after symptom onset and are usually considered for people at higher risk of complications.
    Decisions about antiviral treatment should always be made by a qualified healthcare professional.
    """
)

# General educational notes
add_doc(
    "doc-070",
    "education",
    "Limitations of symptom checkers and chatbots",
    ["flu", "chatbot", "limit"],
    """
    Symptom checkers and chatbots can help people understand whether their symptoms resemble flu or another common condition,
    but they cannot examine a patient, perform tests or make a clinical diagnosis. Their assessments should always be treated
    as rough guidance and never as a replacement for advice from a qualified healthcare professional.
    """
)

add_doc(
    "doc-071",
    "education",
    "Why different people experience flu differently",
    ["flu", "variation", "symptoms"],
    """
    Different people can experience flu quite differently. Age, immune status, underlying health conditions, vaccination history
    and even the specific virus strain can all influence how severe symptoms are and which ones are most prominent.
    This variation is one reason why only a clinician can reliably judge an individual's condition.
    """
)

add_doc(
    "doc-072",
    "education",
    "Flu seasons and community outbreaks",
    ["flu", "season", "epidemic"],
    """
    Flu activity often follows a seasonal pattern, with higher levels in the colder months in many regions.
    During community outbreaks, the probability that a person with fever and cough has flu is higher than when flu activity is low.
    Public health surveillance data can help clinicians interpret symptoms in context.
    """
)

file_path = "flu_rag_corpus.jsonl"
with open(file_path, "w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

len(docs), file_path

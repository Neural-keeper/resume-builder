// --- RESUME TEMPLATE DEFINITION ---
#let resume(
  name: "",
  title: "",
  email: "",
  phone: "",
  github: "",
  linkedin: "",
  site: "",
  body,
) = {
  // Page Setup
  set page(
    paper: "us-letter",
    margin: (x: 1.5cm, y: 1.5cm),
  )
  
  // Font & Text Setup
  set text(
    font: "Liberation Sans", // Fallbacks: "Arial", "Roboto", "Helvetica"
    size: 10pt,
    fill: rgb("#111827"),
  )
  
  // Header Section
  align(center)[
    #text(size: 20pt, weight: "bold")[#name] \
    #v(-2pt)
    #text(size: 11pt, fill: rgb("#4b5563"))[#title] \
    #v(2pt)
    #text(size: 9pt, fill: rgb("#374151"))[
      #list(
        dir: ltr,
        marker: none,
        [📧 #email],
        [📱 #phone],
        if github != "" [#link("https://github.com/" + github)[GitHub]],
        if linkedin != "" [#link("https://linkedin.com/in/" + linkedin)[LinkedIn]],
        if site != "" [#link(site)[Portfolio]],
      )
    ]
  ]

  #v(8pt)
  #body
}

// Custom Section Heading Function
#let section(title) = {
  v(6pt)
  text(size: 11pt, weight: "bold", fill: rgb("#1d4ed8"))[#uppercase(title)]
  v(-4pt)
  line(length: 100%, stroke: 0.8pt + rgb("#d1d5db"))
  v(2pt)
}

// Entry Header Function (Job Title, Company, Date, Location)
#let entry(title, company, dates, location: "") = {
  grid(
    columns: (1fr, auto),
    [*#title* — _#company_], [*#dates*],
  )
  if location != "" {
    text(size: 8.5pt, fill: rgb("#6b7280"))[#location]
    v(2pt)
  }
}

// --- RESUME CONTENT ---

#show: body => resume(
  name: "Alex Mercer",
  title: "Full-Stack Software Engineer",
  email: "alex.mercer@email.com",
  phone: "(555) 019-2831",
  github: "alexmercer",
  linkedin: "alex-mercer",
  site: "https://alexmercer.dev",
  body,
)

#section("Professional Summary")
Adaptable Software Engineer with 4+ years of experience building web applications, microservices, and desktop interfaces. Passionate about performant code, clean UI/UX, and automated tooling.

#section("Work Experience")

#entry(
  "Senior Frontend Engineer",
  "TechCorp Solutions",
  "2022 – Present",
  location: "Austin, TX",
)
- Designed and maintained core dashboard tools serving over 50,000 active daily users.
- Reduced initial bundle load time by 35% through dynamic code splitting and asset optimization.
- Mentored junior developers and led weekly frontend architecture reviews.

#entry(
  "Software Developer",
  "DataPulse Systems",
  "2020 – 2022",
  location: "Remote",
)
- Developed RESTful APIs and asynchronous background tasks using Python and FastAPI.
- Implemented automated CI/CD pipelines reducing deployment friction by 50%.

#section("Projects")

#entry("Local Resume Builder", "Personal Project", "2024")
- Built a local desktop web app using **NiceGUI** and **Typst** for real-time PDF preview and customization.

#section("Skills")
- *Languages:* Python, JavaScript, TypeScript, SQL, HTML/CSS
- *Frameworks & Tools:* NiceGUI, FastAPI, React, Docker, Git, Typst
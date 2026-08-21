"""
Golden Q&A set for the bundled space-exploration corpus.

Each entry maps a natural-language question to the corpus file (`expected_source`,
matching `RetrievedChunk.source`) that contains the answer. `expected_answer` is a
short reference string for future answer-correctness evals; it is not used by the
retrieval eval itself.

`confusable=True` marks questions written to be hard for the retriever — they ask
about a document that shares a topic/entity with one or more sibling documents
(e.g. Apollo 11 vs. Apollo 13 vs. the Apollo program, or Hubble vs. JWST), so a
retriever that leans on generic keyword overlap is more likely to surface the
wrong source for these than for the rest of the set.
"""
from dataclasses import dataclass


@dataclass
class GoldenQA:
    question: str
    expected_source: str
    expected_answer: str
    confusable: bool = False


GOLDEN_QA: list[GoldenQA] = [
    # apollo_11.txt
    GoldenQA(
        "What was the name of the lunar module that Apollo 11 used to land on the Moon?",
        "apollo_11.txt", "Eagle", confusable=True,
    ),
    GoldenQA(
        "Which Apollo 11 astronaut stayed in orbit piloting the command module while the other two walked on the Moon?",
        "apollo_11.txt", "Michael Collins", confusable=True,
    ),
    GoldenQA(
        "How many pounds of lunar material did the Apollo 11 crew collect?",
        "apollo_11.txt", "47.5 pounds",
    ),

    # apollo_13.txt
    GoldenQA(
        "What improvised device did the Apollo 13 crew build from duct tape and plastic covers to remove carbon dioxide?",
        "apollo_13.txt", "\"the mailbox\"", confusable=True,
    ),
    GoldenQA(
        "Who replaced Ken Mattingly on the Apollo 13 crew after his exposure to rubella?",
        "apollo_13.txt", "Jack Swigert", confusable=True,
    ),
    GoldenQA(
        "What crater was Apollo 13 originally scheduled to land near on the Moon?",
        "apollo_13.txt", "Fra Mauro crater",
    ),

    # apollo_program.txt
    GoldenQA(
        "Who championed the lunar orbit rendezvous mission mode adopted for the Apollo program?",
        "apollo_program.txt", "John Houbolt", confusable=True,
    ),
    GoldenQA(
        "How many total missions did the Apollo program complete?",
        "apollo_program.txt", "32", confusable=True,
    ),
    GoldenQA(
        "Which three astronauts died in the Apollo 1 cabin fire?",
        "apollo_program.txt", "Gus Grissom, Ed White, and Roger Chaffee",
    ),

    # artemis_program.txt
    GoldenQA(
        "Which NASA policy directive formally established the Artemis program?",
        "artemis_program.txt", "Space Policy Directive-1",
    ),
    GoldenQA(
        "Which Artemis mission set the record for greatest human distance from Earth, surpassing Apollo 13?",
        "artemis_program.txt", "Artemis II", confusable=True,
    ),
    GoldenQA(
        "As of May 2026, how many countries have signed the Artemis Accords?",
        "artemis_program.txt", "sixty-seven",
    ),

    # falcon_9.txt
    GoldenQA(
        "How many engines power the Falcon 9's first stage, and what is that configuration called?",
        "falcon_9.txt", "nine engines, in an \"Octaweb\" configuration",
    ),
    GoldenQA(
        "What is the record number of flights completed by a single Falcon 9 booster?",
        "falcon_9.txt", "34 flights",
    ),
    GoldenQA(
        "When did the Falcon 9 rocket have its inaugural flight?",
        "falcon_9.txt", "June 4, 2010",
    ),

    # hubble_space_telescope.txt
    GoldenQA(
        "What manufacturing defect was discovered in the Hubble Space Telescope's mirror shortly after launch?",
        "hubble_space_telescope.txt", "spherical aberration", confusable=True,
    ),
    GoldenQA(
        "Who is known as the 'Mother of Hubble' for her advocacy for the telescope's funding?",
        "hubble_space_telescope.txt", "Nancy Grace Roman",
    ),
    GoldenQA(
        "Which Space Shuttle deployed the Hubble Space Telescope into orbit?",
        "hubble_space_telescope.txt", "Discovery",
    ),

    # international_space_station.txt
    GoldenQA(
        "How fast does the International Space Station travel in orbit, in kilometers per second?",
        "international_space_station.txt", "7.67 kilometers per second",
    ),
    GoldenQA(
        "What Russian module began construction of the ISS in November 1998?",
        "international_space_station.txt", "Zarya",
    ),
    GoldenQA(
        "What ISS experiment searches for dark matter?",
        "international_space_station.txt", "the Alpha Magnetic Spectrometer",
    ),

    # james_webb_space_telescope.txt
    GoldenQA(
        "What material coats the 18 hexagonal mirror segments of the James Webb Space Telescope?",
        "james_webb_space_telescope.txt", "gold", confusable=True,
    ),
    GoldenQA(
        "Near which Lagrange point does the James Webb Space Telescope orbit?",
        "james_webb_space_telescope.txt", "the Sun-Earth L2 Lagrange point",
    ),
    GoldenQA(
        "When were the first public images from the James Webb Space Telescope released?",
        "james_webb_space_telescope.txt", "July 11, 2022",
    ),

    # mars_exploration.txt
    GoldenQA(
        "Roughly what percentage of all Mars spacecraft missions have historically failed?",
        "mars_exploration.txt", "about 60%",
    ),
    GoldenQA(
        "Which spacecraft achieved the first successful flyby of Mars?",
        "mars_exploration.txt", "Mariner 4",
    ),
    GoldenQA(
        "What was the name of the first rover to operate on Mars, deployed by the Mars Pathfinder mission?",
        "mars_exploration.txt", "Sojourner", confusable=True,
    ),

    # nasa.txt
    GoldenQA(
        "What organization did NASA succeed when it was established in 1958?",
        "nasa.txt", "the National Advisory Committee for Aeronautics (NACA)",
    ),
    GoldenQA(
        "What Soviet event prompted the urgent creation of NASA?",
        "nasa.txt", "the launch of Sputnik 1",
    ),
    GoldenQA(
        "What was NASA's budget authorized by Congress for fiscal year 2026?",
        "nasa.txt", "$24.4 billion",
    ),

    # perseverance_rover.txt
    GoldenQA(
        "What message was encoded in the pattern of Perseverance's parachute?",
        "perseverance_rover.txt", "\"Dare mighty things\"",
    ),
    GoldenQA(
        "How many flights did the Ingenuity helicopter complete before it was retired?",
        "perseverance_rover.txt", "72 flights", confusable=True,
    ),
    GoldenQA(
        "What rock did Perseverance discover in July 2024 with patterns potentially indicating past biological activity?",
        "perseverance_rover.txt", "\"Cheyava Falls\"",
    ),

    # saturn_v.txt
    GoldenQA(
        "Who directed development of the Saturn V rocket at Marshall Space Flight Center?",
        "saturn_v.txt", "Wernher von Braun",
    ),
    GoldenQA(
        "How many F-1 engines powered the Saturn V's first stage?",
        "saturn_v.txt", "four",
    ),
    GoldenQA(
        "What was the final payload launched by a Saturn V rocket?",
        "saturn_v.txt", "Skylab",
    ),

    # space_shuttle.txt
    GoldenQA(
        "What caused the Space Shuttle Challenger disaster in 1986?",
        "space_shuttle.txt", "an O-ring failure in a solid rocket booster",
    ),
    GoldenQA(
        "What was the name of the mechanical arm Space Shuttle crews used to deploy and retrieve payloads in orbit?",
        "space_shuttle.txt", "Canadarm (the Remote Manipulator System)",
    ),
    GoldenQA(
        "What was the final Space Shuttle mission, and which orbiter flew it?",
        "space_shuttle.txt", "STS-135, flown by Atlantis",
    ),

    # spacex.txt
    GoldenQA(
        "Who founded SpaceX, and in what year?",
        "spacex.txt", "Elon Musk, in 2002",
    ),
    GoldenQA(
        "Which two NASA astronauts were the first to fly aboard SpaceX's Dragon 2 in May 2020?",
        "spacex.txt", "Doug Hurley and Bob Behnken", confusable=True,
    ),
    GoldenQA(
        "What satellite internet constellation does SpaceX operate?",
        "spacex.txt", "Starlink",
    ),

    # voyager_program.txt
    GoldenQA(
        "What photograph did Voyager 1 take in 1990 showing Earth from 6 billion kilometers away?",
        "voyager_program.txt", "the \"Pale Blue Dot\" photograph",
    ),
    GoldenQA(
        "What object do the Voyager spacecraft carry that contains sounds and images meant as a message to other civilizations?",
        "voyager_program.txt", "the Voyager Golden Record",
    ),
    GoldenQA(
        "When did Voyager 1 enter interstellar space?",
        "voyager_program.txt", "August 25, 2012",
    ),
]

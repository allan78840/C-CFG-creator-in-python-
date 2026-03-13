"""
Définitions des nœuds AST pour le langage C
"""

from typing import List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class TypeC(Enum):
    ENTIER = "int"
    FLOTTANT = "float"
    DOUBLE = "double"
    CARACTERE = "char"
    VIDE = "void"
    BOOLEEN = "bool"

class OperateurBinaire(Enum):
    ADDITION = "+"
    SOUSTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"
    MODULO = "%"
    EGAL = "=="
    DIFFERENT = "!="
    INFERIEUR = "<"
    INFERIEUR_EGAL = "<="
    SUPERIEUR = ">"
    SUPERIEUR_EGAL = ">="
    ET_LOGIQUE = "&&"
    OU_LOGIQUE = "||"
    ASSIGNATION = "="

class OperateurUnaire(Enum):
    NEGATIF = "-"
    NON_LOGIQUE = "!"
    PRE_INCREMENTATION = "++(pre)"
    PRE_DECREMENTATION = "--(pre)"
    POST_INCREMENTATION = "++(post)"
    POST_DECREMENTATION = "--(post)"

@dataclass
class Position:
    """Position dans le fichier source"""
    ligne: int
    colonne: int
    
    def __str__(self):
        return f"{self.ligne}:{self.colonne}"

# ============ EXPRESSIONS ============

class Expression:
    """Classe de base pour toutes les expressions"""
    def __init__(self, pos: Optional[Position] = None):
        self.pos = pos

@dataclass
class LitteralEntier(Expression):
    """Littéral entier: 42"""
    valeur: int

@dataclass
class LitteralFlottant(Expression):
    """Littéral flottant: 3.14"""
    valeur: float

@dataclass
class LitteralChaine(Expression):
    """Littéral chaîne: "hello" """
    valeur: str

@dataclass
class LitteralCaractere(Expression):
    """Littéral caractère: 'a' """
    valeur: str

@dataclass
class LitteralBooleen(Expression):
    """Littéral booléen: true/false"""
    valeur: bool

@dataclass
class Identifiant(Expression):
    """Identifiant de variable: x, foo"""
    nom: str

@dataclass
class ExpressionBinaire(Expression):
    """Expression binaire: a + b"""
    gauche: Expression
    operateur: OperateurBinaire
    droite: Expression

@dataclass
class ExpressionUnaire(Expression):
    """Expression unaire: -x, !flag"""
    operateur: OperateurUnaire
    operande: Expression

@dataclass
class AppelFonction(Expression):
    """Appel de fonction: func(a, b)"""
    nom_fonction: str
    arguments: List[Expression]

@dataclass
class AccesTableau(Expression):
    """Accès tableau: arr[i]"""
    tableau: Expression
    indice: Expression

# ============ STATEMENTS ============

class Instruction:
    """Classe de base pour toutes les instructions"""
    def __init__(self, pos: Optional[Position] = None):
        self.pos = pos

@dataclass
class InstructionExpression(Instruction):
    """Instruction expression: x = 5;"""
    expression: Expression

@dataclass
class Declaration(Instruction):
    """Déclaration de variable: int x = 5;"""
    type_variable: TypeC
    nom_variable: str
    initialisateur: Optional[Expression] = None

@dataclass
class Assignation(Instruction):
    """Assignation: x = expr;"""
    cible: Expression  # Variable ou accès tableau
    valeur: Expression

@dataclass
class Bloc(Instruction):
    """Bloc d'instructions: { stmt1; stmt2; }"""
    instructions: List[Instruction]

@dataclass
class InstructionSi(Instruction):
    """Instruction if: if (cond) then_stmt [else else_stmt]"""
    condition: Expression
    instruction_alors: Instruction
    instruction_sinon: Optional[Instruction] = None

@dataclass
class BoucleTantQue(Instruction):
    """Boucle while: while (cond) body"""
    condition: Expression
    corps: Instruction

@dataclass
class BouclePour(Instruction):
    """Boucle for: for (init; cond; update) body"""
    initialisation: Optional[Instruction]
    condition: Optional[Expression] 
    mise_a_jour: Optional[Instruction]
    corps: Instruction

@dataclass
class InstructionRetour(Instruction):
    """Instruction return: return [expr];"""
    valeur: Optional[Expression] = None

@dataclass
class InstructionArret(Instruction):
    """Instruction break"""
    pass

@dataclass
class InstructionContinuer(Instruction):
    """Instruction continue"""
    pass

# ============ DECLARATIONS ============

@dataclass
class Parametre:
    """Paramètre de fonction"""
    type_parametre: TypeC
    nom: str

@dataclass
class DefinitionFonction:
    """Définition de fonction"""
    nom: str
    type_retour: TypeC
    parametres: List[Parametre]
    corps: Instruction
    pos: Optional[Position] = None

@dataclass
class Programme:
    """Programme C complet"""
    fonctions: List[DefinitionFonction]
    
    def obtenir_fonction(self, nom: str) -> Optional[DefinitionFonction]:
        """Cherche une fonction par nom"""
        for fonction in self.fonctions:
            if fonction.nom == nom:
                return fonction
        return None
"""
Analyseur lexical (tokenizer) pour le langage C
"""

import re
from typing import List, Optional, Iterator
from enum import Enum, auto
from dataclasses import dataclass

class TypeJeton(Enum):
    # Littéraux
    LITTERAL_ENTIER = auto()
    LITTERAL_FLOTTANT = auto()
    LITTERAL_CHAINE = auto()
    LITTERAL_CARACTERE = auto()
    LITTERAL_BOOLEEN = auto()
    
    # Identifiants
    IDENTIFIANT = auto()
    
    # Mots-clés
    SI = auto()
    SINON = auto()
    TANT_QUE = auto()
    POUR = auto()
    RETOUR = auto()
    ARRET = auto()
    CONTINUER = auto()
    VRAI = auto()
    FAUX = auto()
    
    # Types
    ENTIER = auto()
    FLOTTANT = auto()
    DOUBLE = auto()
    CARACTERE = auto()
    VIDE = auto()
    BOOLEEN = auto()
    
    # Opérateurs
    PLUS = auto()          # +
    MOINS = auto()         # -
    MULTIPLIER = auto()      # *
    DIVISER = auto()        # /
    MODULO = auto()        # %
    ASSIGNER = auto()        # =
    EGAL = auto()           # ==
    DIFFERENT = auto()           # !=
    INFERIEUR = auto()           # <
    INFERIEUR_EGAL = auto()           # <=
    SUPERIEUR = auto()           # >
    SUPERIEUR_EGAL = auto()           # >=
    ET_LOGIQUE = auto()          # &&
    OU_LOGIQUE = auto()           # ||
    NON_LOGIQUE = auto()          # !
    INCREMENTATION = auto()     # ++
    DECREMENTATION = auto()     # --
    
    # Ponctuation
    POINT_VIRGULE = auto()     # ;
    VIRGULE = auto()         # ,
    PARENTHESE_OUVRANTE = auto()        # (
    PARENTHESE_FERMANTE = auto()        # )
    ACCOLADE_OUVRANTE = auto()        # {
    ACCOLADE_FERMANTE = auto()        # }
    CROCHET_OUVRANT = auto()      # [
    CROCHET_FERMANT = auto()      # ]
    
    # Spéciaux
    FIN_FICHIER = auto()
    NOUVELLE_LIGNE = auto()

@dataclass
class Jeton:
    """Jeton avec type, valeur et position"""
    type: TypeJeton
    valeur: str
    ligne: int
    colonne: int
    
    def __str__(self):
        return f"Jeton({self.type.name}, '{self.valeur}', {self.ligne}:{self.colonne})"

class ErreurAnalyseurLexical(Exception):
    """Exception levée par l'analyseur lexical"""
    def __init__(self, message: str, ligne: int, colonne: int):
        self.message = message
        self.ligne = ligne
        self.colonne = colonne
        super().__init__(f"Erreur analyseur lexical à {ligne}:{colonne}: {message}")

class AnalyseurLexical:
    """Analyseur lexical pour C"""
    
    # Mots-clés
    MOTS_CLES = {
        'if': TypeJeton.SI,
        'else': TypeJeton.SINON,
        'while': TypeJeton.TANT_QUE,
        'for': TypeJeton.POUR,
        'return': TypeJeton.RETOUR,
        'break': TypeJeton.ARRET,
        'continue': TypeJeton.CONTINUER,
        'int': TypeJeton.ENTIER,
        'float': TypeJeton.FLOTTANT,
        'double': TypeJeton.DOUBLE,
        'char': TypeJeton.CARACTERE,
        'void': TypeJeton.VIDE,
        'bool': TypeJeton.BOOLEEN,
        'true': TypeJeton.VRAI,
        'false': TypeJeton.FAUX,
    }
    
    # Opérateurs à deux caractères (à vérifier avant les simples)
    OPERATEURS_DEUX_CARACTERES = {
        '==': TypeJeton.EGAL,
        '!=': TypeJeton.DIFFERENT,
        '<=': TypeJeton.INFERIEUR_EGAL,
        '>=': TypeJeton.SUPERIEUR_EGAL,
        '&&': TypeJeton.ET_LOGIQUE,
        '||': TypeJeton.OU_LOGIQUE,
        '++': TypeJeton.INCREMENTATION,
        '--': TypeJeton.DECREMENTATION,
    }
    
    # Opérateurs à un caractère
    OPERATEURS_UN_CARACTERE = {
        '+': TypeJeton.PLUS,
        '-': TypeJeton.MOINS,
        '*': TypeJeton.MULTIPLIER,
        '/': TypeJeton.DIVISER,
        '%': TypeJeton.MODULO,
        '=': TypeJeton.ASSIGNER,
        '<': TypeJeton.INFERIEUR,
        '>': TypeJeton.SUPERIEUR,
        '!': TypeJeton.NON_LOGIQUE,
        ';': TypeJeton.POINT_VIRGULE,
        ',': TypeJeton.VIRGULE,
        '(': TypeJeton.PARENTHESE_OUVRANTE,
        ')': TypeJeton.PARENTHESE_FERMANTE,
        '{': TypeJeton.ACCOLADE_OUVRANTE,
        '}': TypeJeton.ACCOLADE_FERMANTE,
        '[': TypeJeton.CROCHET_OUVRANT,
        ']': TypeJeton.CROCHET_FERMANT,
    }
    
    def __init__(self, texte: str):
        self.texte = texte
        self.position = 0
        self.ligne = 1
        self.colonne = 1
        self.jetons: List[Jeton] = []
    
    def caractere_actuel(self) -> Optional[str]:
        """Caractère actuel"""
        if self.position >= len(self.texte):
            return None
        return self.texte[self.position]
    
    def regarder_caractere(self, decalage: int = 1) -> Optional[str]:
        """Caractère suivant"""
        position_regarder = self.position + decalage
        if position_regarder >= len(self.texte):
            return None
        return self.texte[position_regarder]
    
    def avancer(self) -> None:
        """Avancer d'un caractère"""
        if self.position < len(self.texte):
            if self.caractere_actuel() == '\n':
                self.ligne += 1
                self.colonne = 1
            else:
                self.colonne += 1
            self.position += 1
    
    def ignorer_espaces(self) -> None:
        """Ignorer les espaces (sauf les nouvelles lignes)"""
        while self.caractere_actuel() and self.caractere_actuel() in ' \t\r':
            self.avancer()
    
    def ignorer_commentaire(self) -> None:
        """Ignorer les commentaires // et /* */"""
        if self.caractere_actuel() == '/' and self.regarder_caractere() == '/':
            # Commentaire ligne entière
            while self.caractere_actuel() and self.caractere_actuel() != '\n':
                self.avancer()
        elif self.caractere_actuel() == '/' and self.regarder_caractere() == '*':
            # Commentaire bloc
            self.avancer()  # /
            self.avancer()  # *
            while self.caractere_actuel():
                if self.caractere_actuel() == '*' and self.regarder_caractere() == '/':
                    self.avancer()  # *
                    self.avancer()  # /
                    break
                self.avancer()
            else:
                raise ErreurAnalyseurLexical("Commentaire non terminé", self.ligne, self.colonne)
    
    def lire_nombre(self) -> Jeton:
        """Lire un nombre (entier ou flottant)"""
        ligne_debut, colonne_debut = self.ligne, self.colonne
        chaine_nombre = ""
        a_point = False
        
        while self.caractere_actuel() and (self.caractere_actuel().isdigit() or self.caractere_actuel() == '.'):
            if self.caractere_actuel() == '.':
                if a_point:
                    break  # Deuxième point, on s'arrête
                a_point = True
            chaine_nombre += self.caractere_actuel()
            self.avancer()
        
        if a_point:
            return Jeton(TypeJeton.LITTERAL_FLOTTANT, chaine_nombre, ligne_debut, colonne_debut)
        else:
            return Jeton(TypeJeton.LITTERAL_ENTIER, chaine_nombre, ligne_debut, colonne_debut)
    
    def lire_chaine(self) -> Jeton:
        """Lire une chaîne "..." """
        ligne_debut, colonne_debut = self.ligne, self.colonne
        self.avancer()  # Ignorer le " ouvrant
        
        valeur_chaine = ""
        while self.caractere_actuel() and self.caractere_actuel() != '"':
            if self.caractere_actuel() == '\\':
                # Caractère d'échappement
                self.avancer()
                if self.caractere_actuel() == 'n':
                    valeur_chaine += '\n'
                elif self.caractere_actuel() == 't':
                    valeur_chaine += '\t'
                elif self.caractere_actuel() == 'r':
                    valeur_chaine += '\r'
                elif self.caractere_actuel() == '\\':
                    valeur_chaine += '\\'
                elif self.caractere_actuel() == '"':
                    valeur_chaine += '"'
                else:
                    valeur_chaine += self.caractere_actuel() or ''
            else:
                valeur_chaine += self.caractere_actuel()
            self.avancer()
        
        if not self.caractere_actuel():
            raise ErreurAnalyseurLexical("Chaîne non terminée", ligne_debut, colonne_debut)
        
        self.avancer()  # Ignorer le " fermant
        return Jeton(TypeJeton.LITTERAL_CHAINE, valeur_chaine, ligne_debut, colonne_debut)
    
    def lire_caractere(self) -> Jeton:
        """Lire un caractère '.' """
        ligne_debut, colonne_debut = self.ligne, self.colonne
        self.avancer()  # Ignorer le ' ouvrant
        
        if not self.caractere_actuel():
            raise ErreurAnalyseurLexical("Caractère non terminé", ligne_debut, colonne_debut)
        
        valeur_caractere = self.caractere_actuel()
        self.avancer()
        
        if self.caractere_actuel() != "'":
            raise ErreurAnalyseurLexical("' fermant attendu", self.ligne, self.colonne)
        
        self.avancer()  # Ignorer le ' fermant
        return Jeton(TypeJeton.LITTERAL_CARACTERE, valeur_caractere, ligne_debut, colonne_debut)
    
    def lire_identifiant(self) -> Jeton:
        """Lire un identifiant ou mot-clé"""
        ligne_debut, colonne_debut = self.ligne, self.colonne
        identifiant = ""
        
        # Premier caractère : lettre ou _
        if self.caractere_actuel() and (self.caractere_actuel().isalpha() or self.caractere_actuel() == '_'):
            identifiant += self.caractere_actuel()
            self.avancer()
        
        # Caractères suivants : lettres, chiffres, _
        while self.caractere_actuel() and (self.caractere_actuel().isalnum() or self.caractere_actuel() == '_'):
            identifiant += self.caractere_actuel()
            self.avancer()
        
        # Vérifier si c'est un mot-clé
        type_jeton = self.MOTS_CLES.get(identifiant, TypeJeton.IDENTIFIANT)
        return Jeton(type_jeton, identifiant, ligne_debut, colonne_debut)
    
    def tokeniser(self) -> List[Jeton]:
        """Tokeniser tout le texte"""
        jetons = []
        
        while self.position < len(self.texte):
            self.ignorer_espaces()
            
            if not self.caractere_actuel():
                break
            
            caractere = self.caractere_actuel()
            ligne_debut, colonne_debut = self.ligne, self.colonne
            
            # Nouvelle ligne
            if caractere == '\n':
                jetons.append(Jeton(TypeJeton.NOUVELLE_LIGNE, caractere, ligne_debut, colonne_debut))
                self.avancer()
                continue
            
            # Commentaires
            if caractere == '/' and (self.regarder_caractere() == '/' or self.regarder_caractere() == '*'):
                self.ignorer_commentaire()
                continue
            
            # Nombres
            if caractere.isdigit():
                jetons.append(self.lire_nombre())
                continue
            
            # Chaînes
            if caractere == '"':
                jetons.append(self.lire_chaine())
                continue
            
            # Caractères
            if caractere == "'":
                jetons.append(self.lire_caractere())
                continue
            
            # Identifiants et mots-clés
            if caractere.isalpha() or caractere == '_':
                jetons.append(self.lire_identifiant())
                continue
            
            # Opérateurs à deux caractères
            deux_caracteres = caractere + (self.regarder_caractere() or '')
            if deux_caracteres in self.OPERATEURS_DEUX_CARACTERES:
                jetons.append(Jeton(self.OPERATEURS_DEUX_CARACTERES[deux_caracteres], deux_caracteres, ligne_debut, colonne_debut))
                self.avancer()
                self.avancer()
                continue
            
            # Opérateurs à un caractère
            if caractere in self.OPERATEURS_UN_CARACTERE:
                jetons.append(Jeton(self.OPERATEURS_UN_CARACTERE[caractere], caractere, ligne_debut, colonne_debut))
                self.avancer()
                continue
            
            # Caractère inconnu
            raise ErreurAnalyseurLexical(f"Caractère inattendu '{caractere}'", ligne_debut, colonne_debut)
        
        # Ajouter fin de fichier
        jetons.append(Jeton(TypeJeton.FIN_FICHIER, "", self.ligne, self.colonne))
        return jetons

def tokeniser(texte: str) -> List[Jeton]:
    """Fonction utilitaire pour tokeniser du texte"""
    analyseur_lexical = AnalyseurLexical(texte)
    return analyseur_lexical.tokeniser()

# Test simple
if __name__ == "__main__":
    code_test = '''
    int factorielle(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorielle(n - 1);
    }
    '''
    
    try:
        jetons = tokeniser(code_test)
        for jeton in jetons[:20]:  # Premiers 20 jetons
            print(jeton)
    except ErreurAnalyseurLexical as e:
        print(f"Erreur: {e}")
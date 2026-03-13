"""
Analyseur syntaxique (parser) pour le langage C
Construit un AST à partir des tokens
"""

from typing import List, Optional, Union
from lexer import Jeton, TypeJeton, ErreurAnalyseurLexical
from ast_nodes import *

class ErreurAnalyseurSyntaxique(Exception):
    """Exception levée par l'analyseur syntaxique"""
    def __init__(self, message: str, jeton: Optional[Jeton] = None):
        self.message = message
        self.jeton = jeton
        if jeton:
            super().__init__(f"Erreur analyseur syntaxique à {jeton.ligne}:{jeton.colonne}: {message}")
        else:
            super().__init__(f"Erreur analyseur syntaxique: {message}")

class AnalyseurSyntaxique:
    """Analyseur syntaxique récursif descendant"""
    
    def __init__(self, jetons: List[Jeton]):
        self.jetons = jetons
        self.position = 0
        self.jeton_actuel = self.jetons[0] if jetons else None
    
    def avancer(self) -> None:
        """Passer au jeton suivant"""
        if self.position < len(self.jetons) - 1:
            self.position += 1
            self.jeton_actuel = self.jetons[self.position]
        else:
            self.jeton_actuel = Jeton(TypeJeton.FIN_FICHIER, "", 0, 0)
    
    def regarder(self, decalage: int = 1) -> Optional[Jeton]:
        """Regarder le jeton à +decalage positions"""
        position_regarder = self.position + decalage
        if position_regarder < len(self.jetons):
            return self.jetons[position_regarder]
        return None
    
    def attendre(self, type_jeton: TypeJeton) -> Jeton:
        """Vérifier que le jeton actuel est du type attendu"""
        if not self.jeton_actuel or self.jeton_actuel.type != type_jeton:
            attendu = type_jeton.name
            actuel = self.jeton_actuel.type.name if self.jeton_actuel else "FIN_FICHIER"
            raise ErreurAnalyseurSyntaxique(f"Attendu {attendu}, obtenu {actuel}", self.jeton_actuel)
        
        jeton = self.jeton_actuel
        self.avancer()
        return jeton
    
    def correspond(self, type_jeton: TypeJeton) -> bool:
        """Vérifier si le jeton actuel correspond au type"""
        return self.jeton_actuel and self.jeton_actuel.type == type_jeton
    
    def ignorer_nouvelles_lignes(self) -> None:
        """Ignorer les nouvelles lignes"""
        while self.correspond(TypeJeton.NOUVELLE_LIGNE):
            self.avancer()
    
    def analyser_position(self) -> Position:
        """Créer une Position à partir du jeton actuel"""
        if self.jeton_actuel:
            return Position(self.jeton_actuel.ligne, self.jeton_actuel.colonne)
        return Position(0, 0)
    
    # PARSING PRINCIPAL 
    def analyser_programme(self) -> Programme:
        """Analyser un programme C complet"""
        fonctions = []
        self.ignorer_nouvelles_lignes()
        
        while not self.correspond(TypeJeton.FIN_FICHIER):
            fonction = self.analyser_fonction()
            fonctions.append(fonction)
            self.ignorer_nouvelles_lignes()
        
        return Programme(fonctions)
    
    def analyser_fonction(self) -> DefinitionFonction:
        """Analyser une définition de fonction"""
        pos = self.analyser_position()
        
        # Type de retour
        type_retour = self.analyser_type()
        
        # Nom de la fonction
        jeton_nom = self.attendre(TypeJeton.IDENTIFIANT)
        nom_fonction = jeton_nom.valeur
        
        # Paramètres
        self.attendre(TypeJeton.PARENTHESE_OUVRANTE)
        parametres = []
        
        if not self.correspond(TypeJeton.PARENTHESE_FERMANTE):
            parametres.append(self.analyser_parametre())
            
            while self.correspond(TypeJeton.VIRGULE):
                self.avancer()  # consommer la virgule
                parametres.append(self.analyser_parametre())
        
        self.attendre(TypeJeton.PARENTHESE_FERMANTE)
        
        # Corps de la fonction
        corps = self.analyser_instruction()
        
        return DefinitionFonction(nom_fonction, type_retour, parametres, corps, pos)
    
    def analyser_parametre(self) -> Parametre:
        """Analyser un paramètre de fonction"""
        type_parametre = self.analyser_type()
        jeton_nom = self.attendre(TypeJeton.IDENTIFIANT)
        return Parametre(type_parametre, jeton_nom.valeur)
    
    def analyser_type(self) -> TypeC:
        """Analyser un type C"""
        if self.correspond(TypeJeton.ENTIER):
            self.avancer()
            return TypeC.ENTIER
        elif self.correspond(TypeJeton.FLOTTANT):
            self.avancer()
            return TypeC.FLOTTANT
        elif self.correspond(TypeJeton.DOUBLE):
            self.avancer()
            return TypeC.DOUBLE
        elif self.correspond(TypeJeton.CARACTERE):
            self.avancer()
            return TypeC.CARACTERE
        elif self.correspond(TypeJeton.VIDE):
            self.avancer()
            return TypeC.VIDE
        elif self.correspond(TypeJeton.BOOLEEN):
            self.avancer()
            return TypeC.BOOLEEN
        else:
            raise ErreurAnalyseurSyntaxique("Type attendu", self.jeton_actuel)
    
    # STATEMENTS 
    
    def analyser_instruction(self) -> Instruction:
        """Analyser une instruction"""
        self.ignorer_nouvelles_lignes()
        pos = self.analyser_position()
        
        if self.correspond(TypeJeton.ACCOLADE_OUVRANTE):
            return self.analyser_bloc()
        elif self.correspond(TypeJeton.SI):
            return self.analyser_instruction_si()
        elif self.correspond(TypeJeton.TANT_QUE):
            return self.analyser_instruction_tant_que()
        elif self.correspond(TypeJeton.POUR):
            return self.analyser_instruction_pour()
        elif self.correspond(TypeJeton.RETOUR):
            return self.analyser_instruction_retour()
        elif self.correspond(TypeJeton.ARRET):
            self.avancer()
            self.attendre(TypeJeton.POINT_VIRGULE)
            instruction = InstructionArret()
            instruction.pos = pos
            return instruction
        elif self.correspond(TypeJeton.CONTINUER):
            self.avancer()
            self.attendre(TypeJeton.POINT_VIRGULE)
            instruction = InstructionContinuer()
            instruction.pos = pos
            return instruction
        elif self.est_jeton_type():
            return self.analyser_declaration()
        else:
            return self.analyser_instruction_expression_ou_assignation()
    
    def analyser_bloc(self) -> Bloc:
        """Analyser un bloc { ... }"""
        pos = self.analyser_position()
        self.attendre(TypeJeton.ACCOLADE_OUVRANTE)
        
        instructions = []
        self.ignorer_nouvelles_lignes()
        
        while not self.correspond(TypeJeton.ACCOLADE_FERMANTE) and not self.correspond(TypeJeton.FIN_FICHIER):
            instruction = self.analyser_instruction()
            instructions.append(instruction)
            self.ignorer_nouvelles_lignes()
        
        self.attendre(TypeJeton.ACCOLADE_FERMANTE)
        
        bloc = Bloc(instructions)
        bloc.pos = pos
        return bloc
    
    def analyser_instruction_si(self) -> InstructionSi:
        """Analyser un if"""
        pos = self.analyser_position()
        self.attendre(TypeJeton.SI)
        self.attendre(TypeJeton.PARENTHESE_OUVRANTE)
        condition = self.analyser_expression()
        self.attendre(TypeJeton.PARENTHESE_FERMANTE)
        
        instruction_alors = self.analyser_instruction()
        
        instruction_sinon = None
        if self.correspond(TypeJeton.SINON):
            self.avancer()
            instruction_sinon = self.analyser_instruction()
        
        instruction_si = InstructionSi(condition, instruction_alors, instruction_sinon)
        instruction_si.pos = pos
        return instruction_si
    
    def analyser_instruction_tant_que(self) -> BoucleTantQue:
        """Analyser un while"""
        pos = self.analyser_position()
        self.attendre(TypeJeton.TANT_QUE)
        self.attendre(TypeJeton.PARENTHESE_OUVRANTE)
        condition = self.analyser_expression()
        self.attendre(TypeJeton.PARENTHESE_FERMANTE)
        corps = self.analyser_instruction()
        
        instruction_tant_que = BoucleTantQue(condition, corps)
        instruction_tant_que.pos = pos
        return instruction_tant_que
    
    def analyser_instruction_pour(self) -> BouclePour:
        """Analyser un for"""
        pos = self.analyser_position()
        self.attendre(TypeJeton.POUR)
        self.attendre(TypeJeton.PARENTHESE_OUVRANTE)
        
        # Initialisation (peut être déclaration ou expression)
        initialisation = None
        if not self.correspond(TypeJeton.POINT_VIRGULE):
            if self.est_jeton_type():
                initialisation = self.analyser_declaration_sans_point_virgule()
            else:
                expr = self.analyser_expression()
                initialisation = InstructionExpression(expr)
        self.attendre(TypeJeton.POINT_VIRGULE)
        
        # Condition
        condition = None
        if not self.correspond(TypeJeton.POINT_VIRGULE):
            condition = self.analyser_expression()
        self.attendre(TypeJeton.POINT_VIRGULE)
        
        # Mise à jour
        mise_a_jour = None
        if not self.correspond(TypeJeton.PARENTHESE_FERMANTE):
            expr = self.analyser_expression()
            mise_a_jour = InstructionExpression(expr)
        self.attendre(TypeJeton.PARENTHESE_FERMANTE)
        
        # Corps
        corps = self.analyser_instruction()
        
        instruction_pour = BouclePour(initialisation, condition, mise_a_jour, corps)
        instruction_pour.pos = pos
        return instruction_pour
    
    def analyser_instruction_retour(self) -> InstructionRetour:
        """Analyser un return"""
        pos = self.analyser_position()
        self.attendre(TypeJeton.RETOUR)
        
        valeur = None
        if not self.correspond(TypeJeton.POINT_VIRGULE):
            valeur = self.analyser_expression()
        
        self.attendre(TypeJeton.POINT_VIRGULE)
        
        instruction_retour = InstructionRetour(valeur)
        instruction_retour.pos = pos
        return instruction_retour
    
    def analyser_declaration(self) -> Declaration:
        """Analyser une déclaration de variable"""
        pos = self.analyser_position()
        type_variable = self.analyser_type()
        jeton_nom = self.attendre(TypeJeton.IDENTIFIANT)
        nom_variable = jeton_nom.valeur
        
        initialisateur = None
        if self.correspond(TypeJeton.ASSIGNER):
            self.avancer()
            initialisateur = self.analyser_expression()
        
        self.attendre(TypeJeton.POINT_VIRGULE)
        
        declaration = Declaration(type_variable, nom_variable, initialisateur)
        declaration.pos = pos
        return declaration
    
    def analyser_declaration_sans_point_virgule(self) -> Declaration:
        """Analyser une déclaration sans point-virgule (pour les for)"""
        pos = self.analyser_position()
        type_variable = self.analyser_type()
        jeton_nom = self.attendre(TypeJeton.IDENTIFIANT)
        nom_variable = jeton_nom.valeur
        
        initialisateur = None
        if self.correspond(TypeJeton.ASSIGNER):
            self.avancer()
            initialisateur = self.analyser_expression()
        
        declaration = Declaration(type_variable, nom_variable, initialisateur)
        declaration.pos = pos
        return declaration
    
    def analyser_instruction_expression_ou_assignation(self) -> Instruction:
        """Analyser expression ou assignation"""
        pos = self.analyser_position()
        expr = self.analyser_expression()
        
        # Vérifier si c'est une assignation
        if self.correspond(TypeJeton.ASSIGNER):
            self.avancer()
            valeur = self.analyser_expression()
            self.attendre(TypeJeton.POINT_VIRGULE)
            
            assignation = Assignation(expr, valeur)
            assignation.pos = pos
            return assignation
        else:
            self.attendre(TypeJeton.POINT_VIRGULE)
            instruction_expression = InstructionExpression(expr)
            instruction_expression.pos = pos
            return instruction_expression
    
    # EXPRESSIONS 
    def analyser_expression(self) -> Expression:
        """Analyser une expression (niveau le plus bas: OR)"""
        return self.analyser_expression_ou()
    
    def analyser_expression_ou(self) -> Expression:
        """Analyser ||"""
        gauche = self.analyser_expression_et()
        
        while self.correspond(TypeJeton.OU_LOGIQUE):
            self.avancer()
            droite = self.analyser_expression_et()
            gauche = ExpressionBinaire(gauche, OperateurBinaire.OU_LOGIQUE, droite)
        
        return gauche
    
    def analyser_expression_et(self) -> Expression:
        """Analyser &&"""
        gauche = self.analyser_expression_egalite()
        
        while self.correspond(TypeJeton.ET_LOGIQUE):
            self.avancer()
            droite = self.analyser_expression_egalite()
            gauche = ExpressionBinaire(gauche, OperateurBinaire.ET_LOGIQUE, droite)
        
        return gauche
    
    def analyser_expression_egalite(self) -> Expression:
        """Analyser == !="""
        gauche = self.analyser_expression_relationnelle()
        
        while self.jeton_actuel and self.jeton_actuel.type in [TypeJeton.EGAL, TypeJeton.DIFFERENT]:
            jeton_operateur = self.jeton_actuel
            self.avancer()
            droite = self.analyser_expression_relationnelle()
            
            if jeton_operateur.type == TypeJeton.EGAL:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.EGAL, droite)
            else:  # DIFFERENT
                gauche = ExpressionBinaire(gauche, OperateurBinaire.DIFFERENT, droite)
        
        return gauche
    
    def analyser_expression_relationnelle(self) -> Expression:
        """Analyser < <= > >="""
        gauche = self.analyser_expression_additive()
        
        while self.jeton_actuel and self.jeton_actuel.type in [TypeJeton.INFERIEUR, TypeJeton.INFERIEUR_EGAL, TypeJeton.SUPERIEUR, TypeJeton.SUPERIEUR_EGAL]:
            jeton_operateur = self.jeton_actuel
            self.avancer()
            droite = self.analyser_expression_additive()
            
            if jeton_operateur.type == TypeJeton.INFERIEUR:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.INFERIEUR, droite)
            elif jeton_operateur.type == TypeJeton.INFERIEUR_EGAL:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.INFERIEUR_EGAL, droite)
            elif jeton_operateur.type == TypeJeton.SUPERIEUR:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.SUPERIEUR, droite)
            else:  # SUPERIEUR_EGAL
                gauche = ExpressionBinaire(gauche, OperateurBinaire.SUPERIEUR_EGAL, droite)
        
        return gauche
    
    def analyser_expression_additive(self) -> Expression:
        """Analyser + -"""
        gauche = self.analyser_expression_multiplicative()
        
        while self.jeton_actuel and self.jeton_actuel.type in [TypeJeton.PLUS, TypeJeton.MOINS]:
            jeton_operateur = self.jeton_actuel
            self.avancer()
            droite = self.analyser_expression_multiplicative()
            
            if jeton_operateur.type == TypeJeton.PLUS:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.ADDITION, droite)
            else:  # MOINS
                gauche = ExpressionBinaire(gauche, OperateurBinaire.SOUSTRACTION, droite)
        
        return gauche
    
    def analyser_expression_multiplicative(self) -> Expression:
        """Analyser * / %"""
        gauche = self.analyser_expression_unaire()
        
        while self.jeton_actuel and self.jeton_actuel.type in [TypeJeton.MULTIPLIER, TypeJeton.DIVISER, TypeJeton.MODULO]:
            jeton_operateur = self.jeton_actuel
            self.avancer()
            droite = self.analyser_expression_unaire()
            
            if jeton_operateur.type == TypeJeton.MULTIPLIER:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.MULTIPLICATION, droite)
            elif jeton_operateur.type == TypeJeton.DIVISER:
                gauche = ExpressionBinaire(gauche, OperateurBinaire.DIVISION, droite)
            else:  # MODULO
                gauche = ExpressionBinaire(gauche, OperateurBinaire.MODULO, droite)
        
        return gauche
    
    def analyser_expression_unaire(self) -> Expression:
        """Analyser expressions unaires: -x, !x, ++x, --x"""
        pos = self.analyser_position()
        
        if self.correspond(TypeJeton.MOINS):
            self.avancer()
            operande = self.analyser_expression_unaire()
            expr = ExpressionUnaire(OperateurUnaire.NEGATIF, operande)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.NON_LOGIQUE):
            self.avancer()
            operande = self.analyser_expression_unaire()
            expr = ExpressionUnaire(OperateurUnaire.NON_LOGIQUE, operande)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.INCREMENTATION):
            self.avancer()
            operande = self.analyser_expression_unaire()
            expr = ExpressionUnaire(OperateurUnaire.PRE_INCREMENTATION, operande)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.DECREMENTATION):
            self.avancer()
            operande = self.analyser_expression_unaire()
            expr = ExpressionUnaire(OperateurUnaire.PRE_DECREMENTATION, operande)
            expr.pos = pos
            return expr
        else:
            return self.analyser_expression_postfixe()
    
    def analyser_expression_postfixe(self) -> Expression:
        """Analyser expressions postfixes: x++, x--, func(), array[i]"""
        gauche = self.analyser_expression_primaire()
        
        while True:
            if self.correspond(TypeJeton.INCREMENTATION):
                self.avancer()
                gauche = ExpressionUnaire(OperateurUnaire.POST_INCREMENTATION, gauche)
            elif self.correspond(TypeJeton.DECREMENTATION):
                self.avancer()
                gauche = ExpressionUnaire(OperateurUnaire.POST_DECREMENTATION, gauche)
            elif self.correspond(TypeJeton.PARENTHESE_OUVRANTE):
                # Appel de fonction
                if isinstance(gauche, Identifiant):
                    self.avancer()  # consommer (
                    arguments = []
                    
                    if not self.correspond(TypeJeton.PARENTHESE_FERMANTE):
                        arguments.append(self.analyser_expression())
                        while self.correspond(TypeJeton.VIRGULE):
                            self.avancer()
                            arguments.append(self.analyser_expression())
                    
                    self.attendre(TypeJeton.PARENTHESE_FERMANTE)
                    gauche = AppelFonction(gauche.nom, arguments)
                else:
                    break
            elif self.correspond(TypeJeton.CROCHET_OUVRANT):
                # Accès tableau
                self.avancer()  # consommer [
                indice = self.analyser_expression()
                self.attendre(TypeJeton.CROCHET_FERMANT)
                gauche = AccesTableau(gauche, indice)
            else:
                break
        
        return gauche
    
    def analyser_expression_primaire(self) -> Expression:
        """Analyser expressions primaires: literals, identifiants, (expr)"""
        pos = self.analyser_position()
        
        if self.correspond(TypeJeton.LITTERAL_ENTIER):
            valeur = int(self.jeton_actuel.valeur)
            self.avancer()
            expr = LitteralEntier(valeur)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.LITTERAL_FLOTTANT):
            valeur = float(self.jeton_actuel.valeur)
            self.avancer()
            expr = LitteralFlottant(valeur)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.LITTERAL_CHAINE):
            valeur = self.jeton_actuel.valeur
            self.avancer()
            expr = LitteralChaine(valeur)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.LITTERAL_CARACTERE):
            valeur = self.jeton_actuel.valeur
            self.avancer()
            expr = LitteralCaractere(valeur)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.VRAI):
            self.avancer()
            expr = LitteralBooleen(True)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.FAUX):
            self.avancer()
            expr = LitteralBooleen(False)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.IDENTIFIANT):
            nom = self.jeton_actuel.valeur
            self.avancer()
            expr = Identifiant(nom)
            expr.pos = pos
            return expr
        elif self.correspond(TypeJeton.PARENTHESE_OUVRANTE):
            self.avancer()
            expr = self.analyser_expression()
            self.attendre(TypeJeton.PARENTHESE_FERMANTE)
            return expr
        else:
            raise ErreurAnalyseurSyntaxique("Expression attendue", self.jeton_actuel)
    
    # ================ UTILITAIRES ================
    
    def est_jeton_type(self) -> bool:
        """Vérifie si le jeton actuel est un type"""
        return self.jeton_actuel and self.jeton_actuel.type in [
            TypeJeton.ENTIER, TypeJeton.FLOTTANT, TypeJeton.DOUBLE,
            TypeJeton.CARACTERE, TypeJeton.VIDE, TypeJeton.BOOLEEN
        ]

def analyser(jetons: List[Jeton]) -> Programme:
    """Fonction utilitaire pour analyser des jetons"""
    analyseur = AnalyseurSyntaxique(jetons)
    return analyseur.analyser_programme()

def analyser_chaine(code: str) -> Programme:
    """Fonction utilitaire pour analyser du code C"""
    from lexer import tokeniser
    jetons = tokeniser(code)
    return analyser(jetons)

# Test simple
if __name__ == "__main__":
    code_test = '''
    int factorielle(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorielle(n - 1);
        }
    }
    '''
    
    try:
        ast = analyser_chaine(code_test)
        print(f"Programme analysé avec {len(ast.fonctions)} fonctions:")
        for fonction in ast.fonctions:
            print(f"  - {fonction.nom}({len(fonction.parametres)} params) -> {fonction.type_retour.value}")
    except (ErreurAnalyseurLexical, ErreurAnalyseurSyntaxique) as e:
        print(f"Erreur: {e}")

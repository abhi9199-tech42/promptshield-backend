
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class PTILNode:
    root: str
    ops: List[str]
    roles: Dict[str, str]
    meta: Optional[str] = None

class PTILEncoder:
    def __init__(self, language: Optional[str] = None):
        self.language = language or "en"
        
        # 0. Pre-cleaning (Long Fluff Removal)
        self.pre_fluff = [
            (re.compile(r'\b(i would like( you)?( to)?|i want( you)?( to)?|i need( you)?( to)?|i am( working on| building| planning| a| an)?)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(can you|could you|would you|will you|please|kindly|i was wondering if|if it\'s not too much trouble)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(would you be so kind as to|i would appreciate it if|i would be grateful if)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(help me|assist me with|tell me|show me)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(is being used for|is for|context is)\b', re.IGNORECASE), "Ctx:"),
            (re.compile(r'\b(act as|you are|pretend to be|imagine you are)\s+(a|an|the)?\b', re.IGNORECASE), ""), 
            (re.compile(r'\b(ensure that|ensure|make sure that|make sure)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(provide|give me)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(what is|what are|how do i|how to)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(i have a|i need a|there is a|there are)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(let me know|let us know)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(feel free to)\b', re.IGNORECASE), ""),
            (re.compile(r'\b(thank you|thanks)\b', re.IGNORECASE), ""),
        ]

        # 2. Intent + Role + Task Normalization Patterns (Step 2)
        self.normalization_patterns = [
            # Intents
            (re.compile(r'\b(create|generate|make|build|construct|produce|writ(e)?)\b', re.IGNORECASE), "mk"),
            (re.compile(r'\b(delete|remove|destroy|erase|discard)\b', re.IGNORECASE), "rm"),
            (re.compile(r'\b(update|modify|change|edit|alter|revise)\b', re.IGNORECASE), "upd"),
            (re.compile(r'\b(explain|describe|clarify|elucidate|interpret)\b', re.IGNORECASE), "expl"),
            (re.compile(r'\b(check|verify|validate|test|assess)\b', re.IGNORECASE), "tst"),
            (re.compile(r'\b(analyze|assess|evaluate|examine)\b', re.IGNORECASE), "eval"),
            (re.compile(r'\b(optimize|improve|enhance|refine|optimiz|improv|enhanc|refin)\b', re.IGNORECASE), "opt"),
            (re.compile(r'\b(calculate|compute|solve|calculat|comput|solv)\b', re.IGNORECASE), "calc"),
            (re.compile(r'\b(search|find|locate|seek)\b', re.IGNORECASE), "find"),
            (re.compile(r'\b(convert|transform|translate)\b', re.IGNORECASE), "conv"),
            
            # Roles & Context
            (re.compile(r'\b(developer|programmer|coder|engineer)\b', re.IGNORECASE), "dev"),
            (re.compile(r'\b(manager|administrator|admin|supervisor)\b', re.IGNORECASE), "admin"),
            (re.compile(r'\b(assistant|helper|support)\b', re.IGNORECASE), "asst"),
            (re.compile(r'\b(student|learner|beginner)\b', re.IGNORECASE), "noob"),
            (re.compile(r'\b(expert|professional|senior)\b', re.IGNORECASE), "pro"),
            
            # Structural/Semantic (Migrated from old patterns)
            (re.compile(r'\b(the script should be|it should be|ensure it is|make sure it)\b', re.IGNORECASE), r""),
            (re.compile(r'\b(include comments to explain|add comments|comment the code)\b', re.IGNORECASE), r"Doc"),
            (re.compile(r'\b(difference between)\b', re.IGNORECASE), "vs"),
            (re.compile(r'\b(in the style of|in the voice of)\b', re.IGNORECASE), "style:"),
            (re.compile(r'\b(step-by-step|step by step)\b', re.IGNORECASE), "steps"),
            (re.compile(r'\b(using|utilizing)\b', re.IGNORECASE), "w/"),
            (re.compile(r'\b(without|excluding)\b', re.IGNORECASE), "w/o"),
            (re.compile(r'\b(including|inclusive of)\b', re.IGNORECASE), "incl"),
            (re.compile(r'\b(regarding|concerning)\b', re.IGNORECASE), "re"),
            (re.compile(r'\b(in order to|so as to)\b', re.IGNORECASE), "to"),
            (re.compile(r'\b(as well as)\b', re.IGNORECASE), "&"),
            (re.compile(r'\b(such as|for example|for instance)\b', re.IGNORECASE), "e.g."),
            (re.compile(r'\b(due to|because of)\b', re.IGNORECASE), "cuz"),
            (re.compile(r'\b(instead of|rather than)\b', re.IGNORECASE), "vs"),
            (re.compile(r'\b(more than|greater than)\b', re.IGNORECASE), ">"),
            (re.compile(r'\b(less than|smaller than)\b', re.IGNORECASE), "<"),
            (re.compile(r'\b(equal to)\b', re.IGNORECASE), "="),
            (re.compile(r'\b(approximately|around|about)\b', re.IGNORECASE), "~"),
            (re.compile(r'\b(percent|percentage)\b', re.IGNORECASE), "%"),
            (re.compile(r'\b(number|count)\b', re.IGNORECASE), "#"),
            (re.compile(r'\b(dollar|usd)\b', re.IGNORECASE), "$"),
            (re.compile(r'\b(and)\b', re.IGNORECASE), "&"),
        ]

        # 3. Stopwords (Aggressive but Safe)
        self.stopwords = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'of', 'to', 'for', 'in', 'on', 'at', 'by', 'from', 'with', 'about',
            'that', 'this', 'these', 'those', 'it', 'its', 'they', 'them', 'my', 'me', 'us', 'our', 'your', 'you',
            'or', 'but', 'so', 'if', 'then', 'else', 'when', 'where', 'why', 'how',
            'very', 'really', 'just', 'also', 'actually', 'basically', 'simply',
            'here', 'there', 'which', 'who', 'whom', 'whose',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'shall', 'should', 'can', 'could', 'may', 'might',
            'please', 'kindly', 'thanks', 'thank', 'hello', 'hi', 'hey',
            'all', 'any', 'some',
            'above', 'below', 'under', 'over', 'again', 'further', 'once',
            'own', 'same', 'than', 'too', 's', 't', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
            'their', 'his', 'her', 'hers', 'him', 'she', 'he',
            'as', 'such', 'like', 'through', 'during', 'before', 'after', 'between', 'among',
            'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
            'allow', 'allows', 'allowing', 'use', 'uses', 'using', 'need', 'needs', 'needing', 'want', 'wants', 'wanting'
        }
        # CRITICAL TOKENS - Explicitly EXCLUDED from stopwords to preserve semantic safety
        # Removed: 'not', 'no', 'yes', 'must', 'don\'t', 'won', 'aren', etc.
        self.critical_tokens = {
            'no', 'not', 'never', 'neither', 'nor', 'none',
            'must', 'always', 'only', 'except', 'unless',
            'critical', 'important', 'warning', 'caution',
            'yes', 'true', 'false'
        }
        self.stopwords_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.stopwords)) + r')\b', re.IGNORECASE)

        # 4. Domain Abbreviations (Post-Root - Expanded for Roots)
        self.abbreviations = {
            'python': 'py', 'javascript': 'js', 'typescript': 'ts',
            'software': 'sw', 'hardware': 'hw',
            'configur': 'cfg', 'configuration': 'cfg', # Rooted & Full
            'lib': 'lib', 'library': 'lib',
            'repo': 'repo', 'repository': 'repo',
            'dir': 'dir', 'directory': 'dir',
            'funct': 'fn', 'function': 'fn', 'fun': 'fn', # Rooted
            'var': 'var', 'variable': 'var',
            'param': 'param', 'parameter': 'param',
            'arg': 'arg', 'argument': 'arg',
            'ret': 'ret', 'return': 'ret',
            'val': 'val', 'value': 'val',
            'str': 'str', 'string': 'str', 
            'int': 'int', 'integer': 'int', 
            'bool': 'bool', 'boolean': 'bool',
            'db': 'db', 'database': 'db',
            'iface': 'iface', 'interface': 'iface',
            'net': 'net', 'network': 'net',
            'app': 'app', 'application': 'app',
            'msg': 'msg', 'message': 'msg',
            'req': 'req', 'request': 'req',
            'res': 'res', 'response': 'res',
            'info': 'info', 'information': 'info',
            'cmd': 'cmd', 'command': 'cmd',
            'tmp': 'tmp', 'temporary': 'tmp',
            'src': 'src', 'source': 'src',
            'dest': 'dest', 'destination': 'dest',
            'prev': 'prev', 'previous': 'prev',
            'nxt': 'nxt', 'next': 'nxt',
            'max': 'max', 'maximum': 'max',
            'min': 'min', 'minimum': 'min',
            'avg': 'avg', 'average': 'avg',
            'rnd': 'rnd', 'random': 'rnd',
            'num': 'num', 'number': 'num',
            'bg': 'bg', 'background': 'bg',
            'img': 'img', 'image': 'img',
            'vid': 'vid', 'video': 'vid',
            'admin': 'admin', 'administrator': 'admin',
            'usr': 'usr', 'user': 'usr',
            'pwd': 'pwd', 'password': 'pwd',
            'cred': 'cred', 'credential': 'cred',
            'auth': 'auth', 'authentication': 'auth', 'authorization': 'auth', 'authentic': 'auth',
            'intl': 'intl', 'international': 'intl',
            'std': 'std', 'standard': 'std',
            'ex': 'ex', 'example': 'ex',
            'algo': 'algo', 'algorithm': 'algo',
            'intro': 'intro', 'introduction': 'intro',
            'conc': 'conc', 'conclusion': 'conc',
            'yr': 'yr', 'year': 'yr',
            'mo': 'mo', 'month': 'mo',
            'hr': 'hr', 'hour': 'hr',
            'min': 'min', 'minute': 'min',
            'sec': 'sec', 'second': 'sec'
        }
        
    def get_root(self, word: str) -> str:
        """
        Simple suffix stripping to find the root of a word.
        Heuristic-based, not a full lemmatizer.
        """
        w = word.lower()
        if len(w) <= 4:
            return word
            
        suffixes = [
            ('ations', ''), ('itions', ''), ('ctions', ''), ('ments', ''),
            ('ation', ''), ('ition', ''), ('ction', ''), ('ment', ''),
            ('ings', ''), ('ing', ''), 
            ('eds', ''), ('ed', ''), 
            ('lys', ''), ('ly', ''), 
            ('ables', ''), ('able', ''), 
            ('full', ''), ('ful', ''), 
            ('less', ''), ('ness', ''), 
            ('ities', ''), ('ity', ''),
            ('est', ''), 
            ('ized', 'ize'), ('ised', 'ise')
        ]
        
        for suffix, replacement in suffixes:
            if w.endswith(suffix):
                # Ensure we don't strip too much (e.g. "sing" -> "s")
                if len(w) - len(suffix) + len(replacement) >= 3:
                    return word[:len(word)-len(suffix)] + replacement
        
        return word

    def encode(self, text: str) -> List[PTILNode]:
        """
        Mock implementation of structural analysis.
        In a real version, this would use dependency parsing.
        """
        # Return a dummy structure for visualization
        return [PTILNode(
            root="Calculate",
            ops=["Fibonacci"],
            roles={"AGENT": "Python Script", "TARGET": "Sequence"},
            meta="Student Project"
        )]

    def apply_cse(self, text: str) -> str:
        """
        Common Subexpression Elimination (CSE).
        Removes repeated sequences of words (bigrams and trigrams) to reduce redundancy.
        Robust to punctuation.
        """
        # Split by non-word characters, keeping delimiters
        tokens = re.split(r'(\W+)', text)
        
        # Identify content tokens (alphanumeric)
        content_indices = [i for i, t in enumerate(tokens) if t.strip() and t[0].isalnum()]
        
        if len(content_indices) < 4:
            return text
            
        to_remove = set()
        seen_trigrams = set()
        seen_bigrams = set()
        
        i = 0
        while i < len(content_indices):
            idx = content_indices[i]
            
            skip_count = 0
            
            # Check Trigram
            if i + 2 < len(content_indices):
                idx2 = content_indices[i+1]
                idx3 = content_indices[i+2]
                trigram = (tokens[idx].lower(), tokens[idx2].lower(), tokens[idx3].lower())
                
                if trigram in seen_trigrams:
                    to_remove.add(idx)
                    to_remove.add(idx2)
                    to_remove.add(idx3)
                    skip_count = 3
                else:
                    seen_trigrams.add(trigram)
            
            if skip_count == 0 and i + 1 < len(content_indices):
                idx2 = content_indices[i+1]
                bigram = (tokens[idx].lower(), tokens[idx2].lower())
                
                if bigram in seen_bigrams:
                    to_remove.add(idx)
                    to_remove.add(idx2)
                    skip_count = 2
                else:
                    seen_bigrams.add(bigram)
            
            if skip_count > 0:
                i += skip_count
            else:
                i += 1
        
        # Reconstruct
        output = []
        for k, token in enumerate(tokens):
            if k in to_remove:
                continue
            output.append(token)
            
        return "".join(output)

    def encode_and_serialize(self, text: str, format: str = "verbose") -> tuple[str, float]:
        """
        Perform aggressive text compression using PTIL patterns.
        Flow: Opt-Out Extraction -> Natural Language -> Semantic ROOT extraction -> Intent/Role Norm -> CSE -> Stopwords -> Abbreviation -> Restore Opt-Out -> Compressed IR
        Returns: (compressed_text, confidence_score)
        """
        # 0. Handle Opt-Out blocks {{ ... }}
        opt_out_blocks = {}
        def opt_out_replacer(match):
            key = f"__OPTOUT_{len(opt_out_blocks)}__"
            opt_out_blocks[key] = match.group(0)
            return key
            
        # Extract {{ content }} and replace with placeholder
        working_text = re.sub(r'\{\{(.*?)\}\}', opt_out_replacer, text, flags=re.DOTALL)
        
        # Calculate initial critical token count for confidence
        lower_input = text.lower()
        input_critical_count = sum(1 for t in self.critical_tokens if re.search(r'\b' + re.escape(t) + r'\b', lower_input))

        compressed = working_text
        
        # 0.1 Pre-cleaning (Long Fluff Removal)
        for pattern, replacement in self.pre_fluff:
            compressed = pattern.sub(replacement, compressed)

        # 1. Semantic ROOT extraction (PTIL)
        tokens = re.split(r'(\W+)', compressed)
        rooted_tokens = []
        for token in tokens:
            if token.strip() and token[0].isalnum() and not token.startswith("__OPTOUT_"):
                rooted_tokens.append(self.get_root(token))
            else:
                rooted_tokens.append(token)
        compressed = "".join(rooted_tokens)

        # 2. Intent + Role + Task normalization
        for pattern, replacement in self.normalization_patterns:
            compressed = pattern.sub(replacement, compressed)
            
        # 2.5 Common Subexpression Elimination (CSE)
        # Skip CSE if it risks merging Opt-Out placeholders (though they are unique)
        compressed = self.apply_cse(compressed)
            
        # 3. Stopwords (Aggressive but Safe)
        compressed = self.stopwords_pattern.sub('', compressed)
        
        # 4. Controlled abbreviation (post-root)
        tokens = re.split(r'(\W+)', compressed)
        abbr_tokens = []
        for token in tokens:
            if not token.strip():
                abbr_tokens.append(token)
                continue
                
            if not token[0].isalnum() or token.startswith("__OPTOUT_"):
                abbr_tokens.append(token)
                continue
                
            lower_token = token.lower()
            if lower_token in self.abbreviations:
                abbr_tokens.append(self.abbreviations[lower_token])
            else:
                abbr_tokens.append(token)
                
        compressed = "".join(abbr_tokens)
        
        # 5. Restore Opt-Out blocks
        for key, value in opt_out_blocks.items():
            compressed = compressed.replace(key, value)
        
        # 6. Final Cleanup
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        compressed = re.sub(r'\s+([,.?!:])', r'\1', compressed)
        compressed = re.sub(r'\s*:\s*', ': ', compressed)
        
        # 7. Calculate Confidence Score
        # Check if critical tokens are preserved in the output
        lower_output = compressed.lower()
        output_critical_count = sum(1 for t in self.critical_tokens if re.search(r'\b' + re.escape(t) + r'\b', lower_output))
        
        # If input had critical tokens, score is ratio of preserved ones.
        # If input had none, score is 1.0 (unless length is suspiciously short?)
        confidence = 1.0
        if input_critical_count > 0:
            confidence = min(1.0, output_critical_count / input_critical_count)
            # Boost confidence slightly if we just replaced them with synonyms (but we don't track synonyms well yet)
            # For now, raw presence check.
            
            # Correction: Some critical tokens might be normalized (e.g., 'not' -> 'not' is preserved).
            # But what if 'ensure that' -> ''? 'ensure' is not in critical.
            # 'must' -> kept.
        
        # Apply slight penalty for extremely aggressive compression if text was long
        if len(text) > 50 and len(compressed) < len(text) * 0.1:
             confidence *= 0.95

        return compressed, confidence

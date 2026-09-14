const PUBLICATIONS_DATA_LOCAL = [
    {
        "title": "Decomposed Attention Frequency Debiased Transformer Model: Large Time-series Model for Satellite Orbit Prediction",
        "authors": [
            "Kanjun Lee",
            "Seungwon Jeong",
            "Jongu Park",
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2026,
        "links": {
            "conf": "https://cikm2026.diag.uniroma1.it/"
        },
        "img": "/img/Publications/2026_CIKM_Kangjun.png",
        "abstract": "Accurate satellite orbit prediction is critical for collision avoidance and sustainable space operations. However, conventional prediction methods are constrained by coarse update intervals and orbit discontinuities. Additionally, building separate prediction models for each satellite is computationally expensive, making large-scale accurate forecasting increasingly impractical. To address the aforementioned challenges, we propose the Decomposed Attention Frequency-debiased transformer (DAF) model, a large time-series prediction model that utilizes efficient Real Fast Fourier Transform (RFFT) and Inverse RFFT alongside positional embeddings. Our DAF also integrates Tensorized Multi-Head Attention based on Tensor Train Decomposition for parameter-efficient compression and improved performance. We pre-trained on a large-scale Starlink dataset comprising 6,955 satellites and evaluated zero-shot performance on seven cross-domain satellite orbit datasets and three real-world datasets. DAF achieves up to 34.85% reduction in mean squared error and 16.01% reduction in mean absolute error over the second-best model, using only 0.045% of its parameters and maintaining inference speed comparable to conventional neural network baselines. These results demonstrate that DAF enables zero-shot, high-precision orbit prediction not only for Starlink satellites, but also for other types of satellites. The code is available here: https://anonymous.4open.science/r/DAF-0D75"
    },
     {
        "title": "FOCAL: Forgery-Centric One-Class Artifact Learning for Out-of-Distribution Deepfake Detection",
        "authors": [
            "Muhammad Shahid Muneer",
            "Razaib Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": "Oral Presentation",
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2026,
        "links": {
            "conf": "https://cikm2026.diag.uniroma1.it/"
        },
        "img": "/img/Publications/2026_CIKM_Shahid.png",
        "abstract": "Existing deepfake detection methods learn facial representations that capture the identity, semantics, or geometric structure of real faces. We argue that such face-centric representations can introduce identity and semantic biases, encoding appearance attributes that correlate with a person’s identity rather than with the image’s manipulation, thereby limiting transferability to unseen forgery types. In this work, we propose Forgery-Centric One-Class Artifact Learning (FOCAL), a representation learning framework that models manipulation artifacts directly rather than generic facial semantics. FOCAL is trained exclusively on forged images: an encoder-decoder reconstructs spatial artifact maps from fake inputs, forcing the encoder to learn where and how manipulation has occurred. This reconstruction objective is complemented by spatial and frequency-domain contrastive losses that encourage invariance to input perturbations while preserving discriminative forgery cues. Because the encoder captures a compact forgery-artifact distribution, real faces unseen during training naturally fall outside. We exploit this property by proposing the Dynamic-Centroid Mahalanobis Distance (DCMD), which enables classifier-free, zero-shot detection without target-domain adaptation. Despite being trained only on fake images, FOCAL surpasses state-of-the-art methods on standard cross-dataset benchmarks in both detection AUC and pixel-level forgery. This clearly demonstrates that forgery-centric representations yield more transferable features than approaches anchored to real-face distributions."
    },
    {
        "title": "Closing Generalization Gaps in Continual Face Forgery Detection",
        "authors": [
            "Bohyun Moon",
            "Minh Binh Le",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": "Oral Presentation",
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2026,
        "links": {
            "conf": "https://cikm2026.diag.uniroma1.it/"
        },
        "img": "/img/Publications/2026_CIKM_Bohyun.png",
        "abstract": "Deepfake manipulations evolve rapidly across digital media platforms, requiring continual updates to detectors as face forgery distributions shift. Unlike general class-incremental learning, continual face forgery detection is a domain-incremental binary task in which new manipulations of the same fake class are introduced. We demonstrate that existing continual deepfake detectors remain tied to distribution-specific cues, preserving performance on seen datasets while struggling to generalize to unseen manipulation domains. We further find that SVD-based parameter-efficient tuning provides a more transferable representation basis but still requires additional regularization to prevent forgetting during sequential updates. Building on these observations, we propose TASER, an exemplar-free continual face forgery detection framework that couples generalized low-rank adaptation with transport-guided representation regularization. Asymmetric Class-Wise Partial Optimal Transport (AC-POT) aligns real and fake manifolds separately for class-aware adaptation, while OT-guided Contrastive Separation (OTCon) strengthens the real/fake boundary using transport-selected positives and opposite-class negatives. TASER achieves state-of-the-art intra-dataset retention and cross-dataset generalization, achieving a final average AUC of 0.9787 with 0.0123 forgetting and an overall cross-dataset AUC of 0.8626 across challenging continual face forgery benchmarks."
    },
    {
        "title": "NullGuard: Null-Space Embedding for Driftless Invisible Image Watermarking",
        "authors": [
            "Inzamamul Alam",
            "Md Tanvir Islam",
            "Juhun Lee",
            "Sangtae Ahn",
            "Simon S. Woo"
        ],
        "venue_full": "British Machine Vision Conference",
        "venue": "BMVC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://bmvc2026.bmva.org/"
        },
        "img": "/img/Publications/2026_BMVC_Inzi.jpg",
        "abstract": "Abstract: Recent progress in text-to-image diffusion highlights the need for invisible, tamper-resilient watermarking that maintains both visual fidelity and prompt alignment. Existing approaches often compromise on robustness, imperceptibility, or scalability, with many introducing semantic drift that weakens provenance guarantees. To address this, we introduce NullGuard, a training-free, plug-and-play watermarking framework that embeds cryptographically keyed signals in the null-space of pretrained diffusion Jacobians, using user-specific rotations to define imperceptible directions. A lightweight Gauss–Newton pivot refinement, constrained by a perceptual mask, perturbs only watermark-relevant components while preserving global semantics, and a calibrated keyed forward likelihood-gap test detects watermarks, achieving up to 99% detection accuracy under attacks such as blurring and JPEG compression, with PSNR $\ge$ 45 dB. Extensive evaluations on MS-COCO and DiffusionDB demonstrate that NullGuard surpasses state-of-the-art (SOTA) methods in robustness, invisibility, and semantic alignment, offering a scalable foundation for provenance-aware diffusion governance."
    },
    {
        "title": "Traffic-IMC: An Urban Road-Network Traffic Forecasting Benchmark",
        "authors": [
            "Seungbin Yim",
            "Hyungchai Park",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems",
        "venue": "SIGSPATIAL",
        "track": "Research Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://sigspatial2026.sigspatial.org/"
        },
        "img": "/img/Publications/ACM SIGSPATIAL_2026_Seungbin.png",
        "abstract": "Accurate traffic forecasting is essential for intelligent transportation systems, yet common benchmarks often focus on highway settings, rely on heavily preprocessed tensors, and offer limited support for studying operational data failures in complex urban road networks. We present Traffic-IMC, an imputation-aware urban traffic-volume forecasting benchmark built from more than three years of hourly measurements from 2,013 quality-controlled road-link sensors in Incheon, South Korea. Traffic-IMC combines traffic records with road-segment metadata and a directed, reachability-aware graph derived from the Korean Standard Node–Link system, enabling evaluation under road directionality, feasible vehicle movements, turn restrictions, and heterogeneous road attributes. Unlike single cleaned releases, Traffic-IMC preserves operational missingness and quality-control invalidations through a frozen validity mask while providing standardized imputed releases for complete model inputs. Its protocol excludes originally missing or invalidated targets from metric computation, enabling controlled analysis of imputation–forecasting pipelines. Baseline results show that urban forecasting accuracy is shaped by the interaction among imputation choices, architectural assumptions, prediction horizons, and physical road-network structure. Traffic-IMC provides a reproducible testbed for diagnosing and improving traffic forecasting in interrupted-flow urban environments. The dataset and source code have been made publicly available at https://github.com/ysb06/traffic-imc."
    },
    {
        "title": "Beyond Attack Success: Trustworthiness Failure Signatures under Adversarial Prompting",
        "authors": [
            "Mirae Kim",
            "Sangyup Lee",
            "Simon S. Woo"
        ],
        "venue_full": "KDD Workshop on Secure and Trustworthy Large Language Models",
        "venue": "SeT-LLM",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": null
        },
        "img": "/img/Publications/2026_SeT-LLM_sangyupLee.png",
        "abstract": "Adversarial attacks against large language models (LLMs) are commonly evaluated through aggregate attack-success metrics, implicitly treating attacks with similar success rates as producing comparable damage. We challenge this assumption by analysing adversarial effects across multiple trustworthiness dimensions—accuracy, safety, confidence, and robustness—and show that attacks induce heterogeneous failure signatures rather than uniform damage. Across five attacks, five benchmarks,and five models, we observe distinct degradation patterns that are not captured by aggregate success metrics. For example, GCG produces negligible accuracy degradation (Δ𝑄 = −0.08) while increasing the unsafe response rate to 90% in a less safety-tuned model, whereas jailbreak rewriting induces both performance degradation and the largest increase in confidently incorrect responses. To investigate the mechanisms behind these outcomes, we further separate observed degradation into multiple failure modes, including protocol-sensitive derailment, safety bypass without proportional capability degradation, and confidence collapse. Our results show that similar apparent attack success can arise from fundamentally different underlying mechanisms. These findings suggest that attack success alone is insufficient for interpreting adversarial outcomes and motivate evaluating attacks through their trustworthiness signatures to support attack-aware evaluation."
    },
    {
        "title": "Anchor-Regularized Adaptation for Generalizable AI-Generated Image Detection with DINOv3",
        "authors": [
            "Hyeongjun Choi",
            "Juhun Lee",
            "Davide Cozzolino",
            "Luisa Verdoliva",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Multimedia",
        "venue": "MM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science=",
            4
        ],
        "year": 2026,
        "links": {
            "conf": "https://2026.acmmm.org/"
        },
        "img": "/img/Publications/2026_ACMMM_hyungjune.png",
        "abstract": "Recent works in AI-generated image detection have shown that careful training data alignment can improve generalization by removing spurious correlations. However, linear probes on frozen DINOv3 representations achieve remarkably strong performance even when trained on misaligned datasets. Motivated by this result, we analyze the underlying rationale and the limits of this generalization. We find that frozen DINOv3 performs well because its decisions rely on features that faithfully represent the space of authentic images. At the same time, its final layer is less effective at capturing the subtle pixel-artifact cues that can be emphasized by aligned training data. We further observe that naively mixing aligned and misaligned data during adaptation improves sensitivity to such cues but at the cost of distorting the pre-trained representation, limiting generalization. To address this issue, we propose Anchor-Regularized Adaptation (ARA). We apply Low-Rank Adaptation to capture pixel-level artifacts while leveraging a frozen anchor classifier to avoid deviations from the original representation structure. This allows the model to exploit pixel-artifact cues without sacrificing generalization. Our method achieves state-of-the-art performance on nine diverse and challenging benchmarks, indicating that ARA enables complementary supervision from misaligned and aligned data for more effective detection."
    },
    {
        "title": "SAVAL: Signal-Driven Adaptive Validation for Post-Silicon Testing via Sequential Decision-Making and Causal-Guided Counterfactual Exploration in NAND Flash Memory",
        "authors": [
            "Sanghyeok Park",
            "Soyoon Park",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/ACM International Conference on Computer-Aided Design",
        "venue": "ICCAD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science=",
            3
        ],
        "year": 2026,
        "links": {
            "conf": "https://iccad.com/2026"
        },
        "img": "/img/Publications/2026_ICCAD_SangHeuk.jpg",
        "abstract": "Post-silicon validation of timing-related defects in advanced 3D NAND flash has become a critical bottleneck due to exhaustive scan evaluation over increasingly complex operation spaces, where defects occur within narrow temporal windows and create a mismatch between sparse failure regions and uniform scan strategies. In this work, we propose SAVAL (Signal-driven Adaptive VALidation), a framework that leverages internal signals (ICC, IVC, ISM) to identify vulnerable intervals and selectively allocate scan effort. SAVAL formulates validation as a sequential decision-making process by integrating hybrid predictive modeling with adaptive exploration, combining deep learning–based temporal feature extraction with tree-based classification and a feedback-driven strategy that balances exploitation of known patterns and discovery of unseen defects. To address the challenge of limited failure observations, we introduce a counterfactual-style exploration mechanism inspired by causal reasoning, which infers failure-prone conditions from pass-dominated signals and guides exploration toward vulnerable regions beyond observed data. Experimental results on industrial 3D NAND datasets demonstrate a 17.8× speedup (94.4% reduction in validation turnaround time) while maintaining 97.5% defect detection accuracy, with 77% alignment to historical defects, highlighting the effectiveness of signal-driven adaptive validation for scalable semiconductor testing. While evaluated on NAND flash memory, the proposed framework is applicable to broader post-silicon validation scenarios across semiconductor systems."
    },
    {
        "title": "Toward trustworthy digital healthcare: A system-level convergence of IoMT, large language models, and explainable AI",
        "authors": [
            "Maria Bashir",
            "Mohammed Abuhamad",
            "Simon S. Woo",
            "Dong In Kim",
            "Tamer Abuhmed"
        ],
        "venue_full": "Information Fusion",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            15.5
        ],
        "year": 2026,
        "links": {
            "conf": "https://www.sciencedirect.com/science/article/pii/S1566253526003866"
        },
        "img": "/img/Publications/2026_InformationFusion_Simon.jpg",
        "abstract": "The Internet of Medical Things (IoMT) enables continuous monitoring, remote diagnosis, and personalized treatment through interconnected medical devices operating across edge, cloud, and local environments. As a communication-centric infrastructure, IoMT depends on interoperability, low-latency networking, and coordinated intelligence to support reliable healthcare services. Realizing its full potential requires computational models that are interpretable, robust, and trustworthy. Large Language Models (LLMs) offer strong capabilities in natural language generation and contextual reasoning for clinical documentation, patient interaction, and decision support, yet their black-box behavior raises concerns regarding transparency and clinical trust. Explainable Artificial Intelligence (XAI) addresses these challenges by providing mechanisms for interpretability and accountability. Although IoMT, LLMs, and XAI have each advanced significantly, prior studies have largely examined them as separate research directions or through limited partial integrations. This work presents a unified system-level analytical study of their convergence in healthcare, positioning IoMT as the foundational infrastructure, LLMs as the contextual reasoning layer, and XAI as the trust-enabling layer for transparency and accountability. Furthermore, the paper systematically examines this convergence through rigorous analysis of architectural foundations and diverse healthcare application domains, and presents clinically grounded case studies to offer a unified, comprehensive, and forward-looking perspective on trustworthy digital healthcare systems."
    },
    {
        "title": "VisionDES: Robust and Explainable Dynamic Vision Ensemble",
        "authors": [
            "Firuz Juraev",
            "Mohammed Abuhamad",
            "Shaker El-Sappagh",
            "Simon S. Woo",
            "Tamer Abuhmed"
        ],
        "venue_full": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "venue": "KDD",
        "track": "Research Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2026,
        "links": {
            "conf": "https://kdd2026.kdd.org/"
        },
        "img": "/img/Publications/2026_KDD_prof.png",
        "abstract": "Dynamic Ensemble Selection (DES) is an adaptive ensemble learning paradigm that selects a subset of base classifiers specific to each test input, enabling more flexible predictions than static ensemble methods. Although successful in tabular settings, DES remains largely unexplored in robust vision applications. We introduce VisionDES, a novel DES framework for image classification that uses deep model embeddings to estimate classifier competence. VisionDES leverages pre-trained vision transformer models to embed inputs and employs approximate nearest neighbor search to define a local region of competence for each sample. It then dynamically selects and fuses the most reliable models, using a similarity-weighted combination that down-weights less reliable or adversarially-compromised classifiers. Our VisionDES is extensively evaluated on various benchmarks and under clean conditions, distribution shifts, and strong adversarial attacks. It consistently outperforms static ensembles and existing uncertainty-based DES methods, improving robust accuracy by up to 20% under strong attacks and 2-3% higher accuracy under distribution shifts, with modest inference overhead. VisionDES offers instance-level interpretability by revealing models' contributions to the final decision."
    },
    {
        "title": "MOSAIV: Multi-Agent LLM Swarms for Automated Multimedia News Verification",
        "authors": [
            "Muhammad Shahid Muneer",
            "Khoa Van Tran",
            "Van Tuan Nguyen",
            "Simon S. woo"
        ],
        "venue_full": "The 2026 Grand Challenge on Multimedia Verification",
        "venue": "ICMR",
        "track": "Demo & Challenge",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://sites.google.com/view/mv2026/task-description"
        },
        "img": "/img/Publications/2026_ICMR_Shahid.png",
        "abstract": "Verifying social media content from active conflict zones requires rapid geolocation, source attribution, forensic analysis, and multi-platform verification—tasks that overwhelm individual analysts at scale. We present Multi-agent OSINT Swarm for Automated Information Verification (MOSAIV), a three-stage agentic swarm built on Large Language Models (LLMs) for automated verification of multimedia news. MOSAIV operates in three sequential phases: (1) a Prime Agent use 50 labeled training samples via few-shot in-context learning to produce a shared context document and a reusable 7-step verification skill specification; (2) multiple parallel Verification Agents each process social media posts using the primed skill, performing live web searches, OSINT analysis, and structured report generation; and (3) a dedicated Localization Agent independently verifies GPS coordinates and produces bounding-box-annotated evidence images, dual-panel OpenStreetMap location cards, and live source evidence thumbnails, multiple evidence artifacts per run in total. We evaluated 10 conflict-zone validation cases provided by the MV2026 challenge."
    },
    {
        "title": "HIDE: Detecting Diffusion-Based Inpainting via Latent h-Space Representation",
        "authors": [
            "Seunghwan ji",
            "Geonho Son",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on Synthetic & Adversarial ForEnsics",
        "venue": "SAFE",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://www.safeworkshop.org/cvpr-2026/#home"
        },
        "img": "/img/Publications/2026_SAFE_Geunho.png",
        "abstract": "The emergence of text-guided diffusion models has enabled highly realistic image inpainting, posing new challenges for image forensics. In particular, diffusion-based inpainting generates semantically coherent and visually seamless content, making forgery localization increasingly difficult. While various detection models have been proposed, they rely on low-level statistical traces that are absent in diffusion-generated content, leaving them ill-equipped for such manipulations. In this work, we propose HIDE (H-space-guided Inpainting DEtection), a Conditional U-Net architecture that leverages multi-domain features including frequency-domain representations, and incorporates high-level semantic priors to detect diffusion-based forgeries. Specifically, we extract h-space features from the intermediate layers of a Latent Diffusion Model, capturing global object layout and scene semantics, and integrate them into a segmentation network via cross-attention. Through extensive experiments on a Stable Diffusion v1.5 inpainting dataset, our findings highlight the importance of jointly exploiting semantic and statistical cues for detecting modern generative inpainting forgeries."
    },
    {
        "title": "Analyzing Commercial Deepfake Detectors on Real-World Cases",
        "authors": [
            "Bohyun Moon",
            "Jiwon Kim",
            "Muhammad Shahid Muneer",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://sites.google.com/view/wdc-2026"
        },
        "img": "/img/Publications/2026_WDC_Bohyun.png",
        "abstract": "The accessibility of generative AI has led to a rapid rise in AI-generated content (AIGC), accompanied by widespread misuse and misinformation. As a result, both researchers and industry have proposed deepfake detection methods, ranging from reproducible academic models to commercial detection services. Commercial deepfake detection tools widely used by many users claim high performance and robustness, while academic tools report strong performance on controlled benchmarks. However, the reliability of both approaches under diverse real-world generation methods remains underexplored. In this work, we perform deepfake detection using both commercial and academic detectors. Our evaluation shows that commercial software tends to achieve stronger out-of-domain generalization than academic baselines. Furthermore, we conduct a case-driven analysis of commercial deepfake detectors with a curated real-world dataset that reflects recent incidents and generation trends. We found that aggregation strategies, mosaic artifacts, and reliance on face detection influence detection decisions, as well as a qualitative analysis of explanation mechanisms. This study identifies structural limitations in current commercial deepfake detection services and proposes potential design directions to enhance robustness in real-world deployment."
    },
    {
        "title": "Efficient Unlearning through Maximizing Relearning Convergence Delay",
        "authors": [
            "Khoa Tran",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
        "venue": "CVPR",
        "track": "Findings Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://cvpr.thecvf.com/Conferences/2026/CallForPapers"
        },
        "img": "/img/Publications/2026_CVPR_KhoaTran.jpg",
        "abstract": "Machine unlearning poses challenges in removing mislabeled, contaminated, or problematic data from a pretrained model. Current unlearning approaches and evaluation metrics are solely focused on model predictions, which limits insight into the model's true underlying data characteristics. To address this issue, we introduce a new metric called relearning convergence delay, which captures both changes in weight space and prediction space, providing a more comprehensive assessment of the model's understanding of the forgotten dataset. This metric can be used to assess the risk of forgotten data being recovered from the unlearned model. Based on this, we propose the Influence Eliminating Unlearning framework, which removes the influence of the forgetting set by degrading its performance and incorporates weight decay and injecting noise into the model's weights, while maintaining accuracy on the retaining set. Extensive experiments show that our method outperforms existing metrics and our proposed relearning convergence delay metric, approaching ideal unlearning performance. We provide theoretical guarantees, including exponential convergence and upper bounds, as well as empirical evidence of strong retention and resistance to relearning in both classification and generative unlearning tasks."
    },

    {
        "title": "Robust Continual Unlearning against Knowledge Erosion and Forgetting Reversal",
        "authors": [
            "EUN-JU PARK",
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
        "venue": "CVPR",
        "track": "Findings Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {
            "conf": "https://cvpr.thecvf.com/Conferences/2026/CallForPapers"
        },
        "img": "/img/Publications/2026_CVPR_EUN-JU PARK.png",
        "abstract": "As a means to balance the growth of the AI industry with the need for privacy protection, machine unlearning plays a crucial role in realizing the ``right to be forgotten'' in artificial intelligence. This technique enables AI systems to remove the influence of specific data while preserving the rest of the learned knowledge. Although it has been actively studied, most existing unlearning methods assume that unlearning is performed only once. In this work, we evaluate existing unlearning algorithms in a more realistic scenario where unlearning is conducted repeatedly, and in this setting, we identify two critical phenomena: (1) Knowledge Erosion, where the accuracy on retain data progressively degrades over unlearning phases, and (2) Forgetting Reversal, where previously forgotten samples become recognizable again in later phases. To address these challenges, we propose SAFER (StAbility-preserving Forgetting with Effective Regularization), a continual unlearning framework that maintains representation stability for retain data while enforcing negative logit margins for forget data. Extensive experiments show that SAFER mitigates not only knowledge erosion but also forgetting reversal, achieving stable performance across multiple unlearning phases."
    },

    {
        "title": "ICR-NET: Robust Deepfake Detection under Temporal Corruption",
        "authors": [
            "Chan Park",
            "Hyeongjun Choi",
            "Shahid Muneer Muhammad",
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "The 30th Pacific-Asia Conference on Knowledge Discovery and Data Mining ",
        "venue": "PAKDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2026,
        "links": {
            "conf": "https://www.pakdd2026.org/"
        },
        "img": "/img/Publications/pakdd26_Chan.png",
        "abstract": "Deepfake video detection aims to distinguish AI-generated facial forgeries from authentic videos. Recent methods have achieved strong performance under spatial corruptions, but their temporal robustness remains largely unexplored. In realistic web-streaming scenarios, network disruptions such as packet loss, bit errors, and aggressive compression induce temporal corruptions that current evaluation protocols and benchmarks do not cover. To cover this gap, we introduce DeepFake Temporal Corruption Benchmark (DF-TCB), built on the standard FaceForensics++ and DFDC video datasets with diverse temporal corruption types and severity levels. Our analysis on DF-TCB reveals that existing detectors are highly fragile under temporal corruptions. We further propose ICR-Net, which predicts frame reliability, selectively corrects corrupted features, and leverages clean–corrupted contrastive learning to obtain corruption-invariant, class-separable representations. We achieve state-of-the-art robustness and cross-dataset generalization under temporal corruptions."
    },
    {
        "title": "A Rich Knowledge Space for Scalable Deepfake Detection",
        "authors": [
            "Inho Jung",
            "Hyeongjun Choi",
            "Binh M. Le",
            "Hohyun Na",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Learning Representations",
        "venue": "ICLR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "",
        ],
        "year": 2026,
        "links": {
            "conf": "https://iclr.cc/Conferences/2026"
        },
        "img": "/img/Publications/ICLR2026_inho.png",
        "abstract": "The proliferation of realistic deepfakes has driven the development of numerous benchmark datasets to support detection research. Despite their increasing volume and diversity, no prior effort has systematically consolidated these resources into a unified framework for large-scale model training, nor has there been a massively pre-trained model tailored to deepfake detection. In this work, we introduce MMI-DD (Multi-modal Multi-type Integrated Deepfake Dataset), a large-scale resource containing 3.6 million facial images, the largest collection to date. It unifies diverse benchmarks with uniform preprocessing, and further provides fine-grained annotations across four deepfake types, as well as VLM-generated descriptions capturing both facial and environmental attributes for each image. By leveraging this comprehensive multi-modal dataset, we construct a foundational deepfake knowledge space that empowers our model to discern a broad spectrum of synthetic media. Our method, SD^2 (Scalable Deepfake Detection), refines CLIP for deepfake detection, optimizing image-text classification with rich, type-specific labels. We enhance this with intermediate visual features capturing low-level cues and text label separation loss for stability. We further leverage VLM-generated descriptions and contrastive learning to expand the scope of forgery knowledge, reducing overfitting and enhancing generalization. Extensive experiments on challenging deepfake datasets and AIGC benchmark demonstrate the effectiveness, scalability, and real-world applicability of our approach."
    },
    {
        "title": "Unlearning Comparator: A Visual Analytics System for Comparative Evaluation of Machine Unlearning Methods",
        "authors": [
            "Jaeung Lee",
            "Suhyeon Yu",
            "Yurim Jang",
            "Simon S. Woo",
            "Jaemin Jo"

        ],
        "venue_full": "IEEE Transactions on Visualization and Computer Graphics",
        "venue": "TVCG",
        "track": null,
        "Factor": [
            "SCI IF=",
            6.5
        ],
        "year": 2026,
        "links": {
            "conf": "https://www.computer.org/csdl/journal/tg"
        },
        "img": "/img/Publications/TVCG26_yurim.png",
        "abstract": "Machine Unlearning (MU) aims to remove target training data from a trained model so that the removed data no longer influences the model's behavior, fulfilling \"right to be forgotten\" obligations under data privacy laws. Yet, we observe that researchers in this rapidly emerging field face challenges in analyzing and understanding the behavior of different MU methods, especially in terms of three fundamental principles in MU: accuracy, efficiency, and privacy. Consequently, they often rely on aggregate metrics and ad-hoc evaluations, making it difficult to accurately assess the trade-offs between methods. To fill this gap, we introduce a visual analytics system, Unlearning Comparator, designed to facilitate the systematic evaluation of MU methods. Our system supports two important tasks in the evaluation process: model comparison and attack simulation. First, it allows the user to compare the behaviors of two models, such as a model generated by a certain method and a retrained baseline, at class-, instance-, and layer-levels to better understand the changes made after unlearning. Second, our system simulates membership inference attacks (MIAs) to evaluate the privacy of a method, where an attacker attempts to determine whether specific data samples were part of the original training set. We evaluate our system through a case study visually analyzing prominent MU methods and demonstrate that it helps the user not only understand model behaviors but also gain insights that can inform the improvement of MU methods."
    },
    {
        "title": "Suppression or Deletion: A Restoration-Based Representation-Level Analysis of Machine Unlearning",
        "authors": [
            "Yurim Jang",
            "Jaeung Lee",
            "Dohyun Kim",
            "Jaemin Jo",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2026,
        "links": {
            "conf": "https://www2026.thewebconf.org/"
        },
        "img": "/img/Publications/WWW2026short_yurim.png",
        "abstract": "As pretrained models are increasingly shared on the web, ensuring that models can forget or delete sensitive, copyrighted, or private information upon request has become crucial. Machine unlearning has been proposed to address this issue. However, current evaluations for unlearning methods rely on output-based metrics, which cannot verify whether information is completely deleted or merely suppressed at the representation level, where suppression is insufficient for true unlearning. To address this gap, we propose a novel restoration-based analysis framework that uses Sparse Autoencoders to identify class-specific expert features in intermediate layers and applies inference-time steering to quantitatively distinguish between suppression and deletion. Applying our framework to 12 major unlearning methods in image classification tasks, we find that most methods achieve high restoration rates of unlearned information, indicating that they only suppress information at the decision-boundary level, while preserving semantic features in intermediate representations. Notably, even retraining from pretrained checkpoints shows high restoration, revealing that pretrained feature hierarchies persist. These results demonstrate that representation-level retention poses significant risks overlooked by output-based metrics, highlighting the need for new unlearning evaluation criteria. We propose new evaluation guidelines that prioritize representation-level verification, especially for privacy-critical applications in the pretrained model era."
    },
    {
        "title": "Toward Data-Driven Satellite Orbit Prediction: A Dataset and Method Survey for Multi-Regime Satellites",
        "authors": [
            "Kangjun Lee",
            "Seungwon Jeong",
            "JongU Park",
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIED IF =",
            4.2
        ],
        "year": 2026,
        "links": {
            "conf": "https://ieeexplore.ieee.org/document/11594093"
        },
        "img": "/img/Publications/2026_IEEE_KangJun.png",
        "abstract": "The rapid proliferation of artificial satellites and space debris necessitates accurate orbit prediction to ensure orbital sustainability. While machine learning has emerged as a powerful tool for this task, existing surveys lack a systematic investigation into the critical relationship between orbital regimes (LEO, MEO, and GEO) and dataset characteristics. This paper presents a comprehensive survey of data-driven satellite orbit prediction, offering a novel taxonomy centered on the datasets that underpin these studies. We systematically analyze how distinct orbital dynamics and data formats, ranging from Two-Line Elements (TLEs) to precise ephemerides, affect predictive model performance, and we categorize the models into hybrid and non-hybrid approaches that leverage machine learning and deep learning. Furthermore, we identify significant limitations in current research, particularly the lack of model generalization across diverse missions and the imbalance of available data. Finally, we propose future research directions, advocating the development of foundation models and the curation of high-fidelity, multi-regime datasets to advance the field toward universal orbit prediction."
    },
    {
        "title": "Fitting Image Diffusion Models on Video Datasets",
        "authors": [
            "Juhun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "Workshop on International Conference on Computer Vision",
        "venue": "ICCV",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {
            "conf": "https://iccv.thecvf.com/"
        },
        "img": "/img/Publications/2025_ICCVW_Juhun.png",
        "abstract": "Image diffusion models are trained on independently sampled static images. While this is the bedrock task protocol in generative modeling, capturing the temporal world through the lens of static snapshots is information-deficient by design. This limitation leads to slower convergence, limited distributional coverage, and reduced generalization. In this work, we propose a simple and effective training strategy that leverages the temporal inductive bias present in continuous video frames to improve diffusion training. Notably, the proposed method requires no architectural modification and can be seamlessly integrated into standard diffusion training pipelines. We evaluate our method on the HandCo dataset, where hand-object interactions exhibit dense temporal coherence andsubtle variations in finger articulation often result in semantically distinct motions. Empirically, our method accelerates convergence by over 2x faster and achieves lower FID on both training and validation distributions. It also improves generative diversity by encouraging the model to capture meaningful temporal variations. We further provide an optimization analysis showing that our regularization reduces the gradient variance, which contributes to faster convergence."
    },
    {
        "title": "Self-Disclosure of Mental Health via Deepfakes: Testing the Effects of Self-Deepfakes on Affective Resistance and Intention to Seek Mental Health Support",
        "authors": [
            "Jiyoung Lee",
            "Christopher M Dobmeier",
            "Minji Heo",
            "Simon S. Woo"
        ],
        "venue_full": "Health Communication",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "SSCI IF=",
            2.7
        ],
        "year": 2025,
        "links": {
            "conf": "https://www.tandfonline.com/journals/hhth20"
        },
        "img": "/img/Publications/2025_minji_health_communication.png",
        "abstract": "This study examines the use of deepfakes in self-disclosure interventions within mental health contexts. Specifically, we investigate how videos featuring self-deepfakes, celebrity deepfakes, and virtual agents disclosing mental health challenges shape affective resistance and intention to seek support, considering the moderating influence of individual baseline mental health. The findings indicate that self-deepfakes elicited greater affective resistance than celebrity deepfakes, leading to reduced help-seeking intention, whereas no significant differences were observed between self-deepfakes and virtual agent disclosures. Also, the moderation analysis showed that participants with lower baseline mental health were especially prone to heightened affective resistance toward self-disclosure videos featuring deepfake representations of themselves. Our findings indicate that artificial intelligence (AI)-generated self-deepfakes, which personalize content without affording users agency, may reverse the conventional self-referencing effect, provoking affective resistance rooted in identity threat. Since these counterproductive effects are most salient among individuals with negative self-schemas who struggle with greater mental health challenges, AI-driven technologies should be applied in health communication with caution, accompanied by tailored strategies designed to curb impulsive, emotion-driven resistance."
    },
    {
        "title": "TwinTCN: Correlation-Gated Temporal Convolutions with Twin Encoders",
        "authors": [
            "Yong-Cheol Ro",
            "Simon S. Woo"
        ],
        "venue_full": "ACM/SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Machine Learning and Its Application (MLA)",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2026,
        "links": {
            "conf": "https://www.sigapp.org/sac/sac2026/"
        },
        "img": "/img/Publications/SAC-MLA_2026_YongCheolRo.png",
        "abstract": "Along with the global trend of electric vehicle adoption, robust fault detection in EV battery management systems (BMS) is becoming increasingly important. In particular, fault detection in electric vehicles poses significant challenges to conventional methods due to non-stationarity, multi-scale dynamics, and label scarcity. We propose a correlation-aware \emph{TwinTCN} with \emph{RF-aligned} gating that matches correlation windows to TCN receptive fields, and couple it with a twin-encoder contrastive objective plus reconstruction to enhance discriminability while preserving normal patterns. Across three real-world EV datasets, the proposed model attains the highest \(F_1\) with a balanced precision–recall profile, outperforming unsupervised, supervised, and semi-supervised baselines."
    },
    {
        "title": "Exploring Gemini 2.5 for Explainable Deepfake Detection under Black-Box Constraints",
        "authors": [
            "Hyunjune Kim",
            "Hyeongjun Choi",
            "Simon S. Woo"
        ],
        "venue_full": "CIKM Workshop on Human-Centric AI: From Explainability and Trustworthiness to Actionable Ethics",
        "venue": null,
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {
            "conf": "https://xai.kaist.ac.kr/Workshop/hcai2025/"
        },
        "img": "/img/Publications/CIKM-W2026_HyunjuneKim.png",
        "abstract": "The rapid advancement of deepfake generation poses significant challenges for reliable media verification. Effective detection increasingly demands methods that are both accurate and interpretable, motivating the use of multimodal large language models (MLLMs) for transparency and human-aligned explainability. While prior work has primarily focused on open-source MLLMs, we investigate, for the first time, the potential of a closed-source model, Google Gemini 2.5, for deepfake detection and explanation. We systematically evaluate Gemini via zero-shot testing and adapter-based black-box fine-tuning using Google Vertex AI. On a simple binary dataset (FaceForensics++), zero-shot performance is low and fine-tuning yields only modest gains. Remarkably, on a vision-language benchmark (DD-VQA), even straightforward black-box fine-tuning enables Gemini to outperform existing state-of-the-art models, highlighting the dataset-dependent impact of fine-tuning on closed-source models. Our study empirically demonstrates the feasibility of explainable deepfake detection using closed-source MLLMs, revealing both their promise and current limitations."
    },
    {
        "title": "From Rules to LLM-Enhanced Templates: A Hybrid ALPG Code Generation System",
        "authors": [
            "Sanghyeok Park",
            "Sungjea Hwang",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Software Engineering",
        "venue": "ICSE-SEIP",
        "track": "Industry Paper",
        "presentationType": null,
        "Factor": ["",
            0
        ],
        "year": 2026,
        "links": {},
        "img": "/img/Publications/ICSE-SEIP2026_SangHyeokPark.png",
        "abstract": "The semiconductor industry operates as a multidisciplinary environment where engineers face development challenges due to varying coding proficiency. ALPG (Algorithmic Pattern Generator), used in semiconductor test equipment, requires nanosecond-level timing precision and signal control, yet existing LLMs fail to generate proper ALPG code due to the absence of public datasets. To address these challenges, we first developed RuleLang, a rule-based system achieving 76.3% coverage across 271 ALPG test patterns, but revealing limitations in handling new combinations. We then propose a hybrid system where LLMs generate JSON templates that are parsed by rule-based parsers into executable ALPG code. By constraining LLM outputs to schema-validated JSON, the system mitigates probabilistic uncertainty and prevents unsafe direct code generation. Evaluation on 271 real-world ALPG test patterns from Samsung’s 8th-generation V-NAND Flash memory achieved 84.2% accuracy, including a 23.4%p gain on new sequence test patterns, demonstrating significant improvements over manual and rule-based development."
    },
    {
        "title": "CelebCaption: A Benchmark Dataset for Identity-Sensitive Unlearning in Image Captioning",
        "authors": [
            "Hakjun Moon",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Web Search and Data Mining",
        "venue": "WSDM",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2026,
        "links": {},
        "img": "/img/Publications/WSDM2026_HakjunMoon.png",
        "abstract": "Machine unlearning seeks to remove the influence of selected training examples without retraining the model from scratch. Recent work has extended this goal to vision–language models, yet existing datasets are not suited for judging whether a sample’s influence has truly been erased from learned image–text pairs. Current algorithms often intend to introduce false information into sentences generated after unlearning, which compromises utility. We first establish three criteria that an image-caption unlearning method should meet: Specificity Reduction, Identity Removal, and Performance Preservation. Guided by these criteria, we present CelebCaption, an image–text dataset of 15,000 photographs covering 150 well-known individuals, each linked to four captions that vary in detail (detailed vs. summary) and in the presence of the subject’s name. This design enables controlled, quantitative assessment of the proposed unlearning objectives. We benchmark several representative unlearning algorithms on CelebCaption, using both caption quality scores and MIA accuracy as a quantitative unlearning metric, and observe that current methods fail to achieve their privacy objectives. Our unlearning criteria and dataset provide a focused, reproducible testbed for advancing privacy-aware image captioning. Our CelebCaption dataset is publicly available at https://github.com/Gloriel621/CelebCaption"
    },

    {
        "title": "Machine Pareidolia: Protecting Facial Images with Emotional Editing",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "AAAI Conference on Artificial Intelligence",
        "venue": "AAAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2026,
        "links": {},
        "img": "/img/Publications/aaai2026_binhle.gif",
        "abstract": "The proliferation of facial recognition (FR) systems has raised privacy concerns in the digital realm, as malicious uses of FR models pose a significant threat. Traditional countermeasures, such as makeup style transfer, have suffered from low transferability in black-box settings and limited applicability across various demographic groups, including males and individuals with darker skin tones. To address these challenges, we introduce a novel facial privacy protection method, dubbed MAP, a pioneering approach that employs human emotion modifications to disguise original identities as target identities in facial images. Our method uniquely fine-tunes a score network to learn dual objectives, target identity and human expression, which are jointly optimized through gradient projection to ensure convergence at a shared local optimum. Additionally, we enhance the perceptual quality of protected images by applying local smoothness regularization and optimizing the score matching loss within our network. Empirical experiments demonstrate that our innovative approach surpasses previous baselines, including noise-based, makeup-based, and freeform attribute methods, in both qualitative fidelity and quantitative metrics. Furthermore, MAP proves its effectiveness against an online FR API and shows advanced adaptability in uncommon photographic scenarios."
    },
    {
        "title": "AEON: Adaptive Embedding Optimized Noise for Robust Watermarking in Diffusion Models",
        "authors": [
            "Muhammad Shahid Muneer",
            "Simon S. Woo"
        ],
        "venue_full": "The IEEE/CVF Winter Conference on Applications of Computer Vision",
        "venue": "WACV",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2026,
        "links": {},
        "img": "/img/Publications/2026_WACV_Shahid_AEON.jpg",
        "abstract": "The widespread use of synthetic image generation models and the challenges associated with authenticity preservation have fueled the demand for robust watermarking methods to safeguard authenticity and protect the copyright of synthetic images. Existing watermarking methods embed. Invisible signatures in synthetic images often compromise image quality and remain susceptible to multiple watermark removal attacks, including reconstruction and forgery methods. To overcome this issue, we propose a novel watermarking approach, AEON, which seamlessly integrates the watermark into the latent diffusion process and ensures the watermark aligns with scene semantics in the final image. Unlike existing invisible in-diffusion watermarking and traditional hash-based methods, our approach adapts the neural synthesized hash-based watermark to the semantics of the generated image during the intermediate diffusion process instead of embedding traditional hashes with the initial noise. This facilitates visual coherence in the generated image while enhancing adversarial robustness and resilience against single or multiple adversarial and traditional watermark removal attacks. Our proposed approach a) modulates the noise sampling in each diffusion denoising iteration through a learnable watermark embedding, b) optimizes consistency, reconstruction, and similarity loss, enforcing local and global alignment between the watermark structure and the underlying image content, and c) generates a strong watermark by allowing late embedding of the watermark in the diffusion process. Empirical results demonstrate the effectiveness of the proposed approach in retaining quality and its robustness against cumulative adversarial attacks."
    },
    {
        "title": "RUAGO: Effective and Practical Retain-Free Unlearning via Adversarial Attack and OOD Generator",
        "authors": [
            "Sangyong Lee",
            "Sangjun Chung",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Neural Information Processing Systems",
        "venue": "NeurIPS",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/nips2025_sangyong.jpg",
        "abstract": "With increasing regulations on private data usage in AI systems, machine unlearning has emerged as a critical solution for selectively removing sensitive information from trained models while preserving their overall utility. While many existing unlearning methods rely on the retain data to mitigate the performance decline caused by forgetting, such data may not always be available (retain-free) in real-world scenarios. To address this challenge posed by retain-free unlearning, we introduce RUAGO, utilizing adversarial soft labels to mitigate over-unlearning and a generative model pretrained on out-of-distribution (OOD) data to effectively distill the original model’s knowledge. We introduce a progressive sampling strategy to incrementally increase synthetic data complexity, coupled with an inversion-based alignment step that ensures the synthetic data closely matches the original training distribution. Our extensive experiments on multiple benchmark datasets and architectures demonstrate that our approach consistently outperforms existing retain-free methods and achieves comparable or superior performance relative to retain-based approaches, demonstrating its effectiveness and practicality in real-world, data-constrained environments."
    },
    {
        "title": "Through the Lens: Benchmarking Deepfake Detectors Against Moiré-Induced Distortions",
        "authors": [
            "Razaib Tariq",
            "Minji Heo",
            "Simon S. Woo",
            "Shahroz Tariq"
        ],
        "venue_full": "Conference on Neural Information Processing Systems",
        "venue": "NeurIPS",
        "track": "Dataset Paper",
        "presentationType": "Poster Presentation",
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/neurips-25-Razaib.png",
        "abstract": "Deepfake detection remains a pressing challenge, particularly in real-world settings where smartphone-captured media from digital screens often introduces Moiré artifacts that can distort detection outcomes. This study systematically evaluates state-of-the-art (SOTA) deepfake detectors on Moiré-affected videos an issue that has received little attention. We collected a dataset of 12,832 videos, spanning 35.64 hours, from Celeb-DF, DFD, DFDC, UADFV, and FF++ datasets, capturing footage under diverse real-world conditions, including varying screens, smartphones, lighting setups, and camera angles. To further examine the influence of Moiré patterns on deepfake detection, we conducted additional experiments using our DeepMoiréFake, referred to as (DMF) dataset, and two synthetic Moiré generation techniques. Across 15 top-performing detectors, our results show that Moiré artifacts degrade performance by as much as 25.4%, while synthetically generated Moiré patterns lead to a 21.4% drop in accuracy. Surprisingly, demoiréing methods, intended as a mitigation approach, instead worsened the problem, reducing accuracy by up to 16%. These findings underscore the urgent need for detection models that can robustly handle Moiré distortions alongside other real-world challenges, such as compression, sharpening, and blurring. By introducing the DMF dataset, we aim to drive future research toward closing the gap between controlled experiments and practical deepfake detection."
    },
    {
        "title": "FakeChain: Exposing Shallow Cues in Multi-Step Deepfake Detection",
        "authors": [
            "Minji Heo",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/2025_CIKM_minji.PNG",
        "abstract": "Multi-step or hybrid deepfakes, generated through successively applying different deepfake creation methods such as face-swapping, GAN-based generation, and Diffusion refinement, can pose an emerging challenge for detection models trained on single-step forgeries. While prior studies focus on isolated manipulations, little is known about model behavior under such compositional manipulation pipelines. In this work, we introduce FakeChain, a large-scale benchmark comprising 1-, 2-, and 3-Step manipulated face images synthesized using five state-of-the-art generators, including face-swap, GAN, and Diffusion models. Using this dataset, we analyze detection performance and spectral properties across manipulation depths, generator combinations, and quality settings. Our findings reveal that detection performance highly depends on the final manipulation step, with F1-score dropping by up to 58.83% when it differs from training. Detectors rely on shallow cues from the last stage, limiting generalization across multi-step forgeries. We also observe architectural differences in robustness to compression, with attention-based models being more sensitive than CNN-based ones. These insights highlight the need for detection models that account for manipulation history and benchmarks such as FakeChain that reflect the evolving nature of deepfake synthesis pipelines. We share some sample of our code here."
    },
    {
        "title": "Seeing Through the Blur: Unlocking Defocus Maps for Deepfake Detection",
        "authors": [
            "Minsun Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/DoF_G.png",
        "abstract": "The rapid advancement of generative AI has enabled the mass production of photorealistic synthetic images, blurring the boundary between authentic and fabricated visual content. This challenge is particularly evident in deepfake scenarios involving facial manipulation, but also extends to broader AI-generated content (AIGC) cases that feature fully synthesized scenes. As such content becomes increasingly difficult to distinguish from reality, the integrity of visual media is undergoing threat. To address this issue, we propose a physically interpretable deepfake detection framework and demonstrate that defocus blur can serve as an effective forensic signal. Defocus blur is a depth-dependent optical phenomenon that naturally occurs in camera-captured images due to lens focus and scene geometry. In contrast, synthetic images often lack realistic depth-of-field (DoF) characteristics, resulting in globally sharp or physically inconsistent blur patterns. To capture these discrepancies, we construct a defocus blur map and use it as a discriminative feature for detecting manipulated content. Our approach is supported by three in-depth feature analyses, and experimental results confirm that defocus blur provides a reliable and interpretable cue for identifying synthetic images. We aim for our defocus-based detection pipeline and interpretability tools to contribute meaningfully to ongoing research in media forensics."
    },
    {
        "title": "Anomaly Detection for Advanced Driver Assistance System with NCDE-based Normalizing Flow",
        "authors": [
            "Kangjun Lee",
            "Minha Kim",
            "Youngho Jun",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/2025CIKM_kangjun_minha.png",
        "abstract": "For electric vehicles, the Adaptive Cruise Control (ACC) in Advanced Driver Assistance Systems (ADAS) is designed to assist braking based on driving conditions and user patterns. However, the driving data collected during development are limited and lack diversity, leading to late or aggressive braking. Moreover, it is necessary to effectively identify anomalies in braking patterns, which is critical for self-driving autonomous vehicles. We propose Graph Neural Controlled Differential Equation Normalizing Flow (GDFlow), which leverages Normalizing Flow (NF) with Neural Controlled Differential Equations (NCDE) to learn the distribution of normal driving patterns. Our approach captures spatio-temporal information from sensor data and accurately models continuous changes in driving patterns. Additionally, we introduce a quantilebased maximum likelihood objective to improve the likelihood estimate of normal data at the margin of the distribution. We validate GDFlow using real-world electric vehicle driving data that we collected from Hyundai IONIQ5 and GV80EV. Our model achieves state-of-the-art (SOTA) performance compared to nine baselines across four dataset configurations of different vehicle types and drivers. Furthermore, our model outperforms the latest anomaly detection methods across four time series benchmark datasets. Our approach demonstrates superior efficiency in inference time compared to existing methods. We plan to deploy GDFlow in the Hyundai Genesis GV90 by March 2026."
    },
    {
        "title": "MU-OT: Effective and Unified Machine Unlearning with Optimal Transport for Feature Realignment",
        "authors": [
            "Sangjun Chung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/2025_CIKM_sangjun.jpg",
        "abstract": "Machine unlearning has emerged as a significant research topic in response to the increasing demands for data privacy and compliance with privacy regulations. The main challenge is to eliminate the influence of a specific subset of training data from a pretrained model while preserving the model’s performance on the retain set without retraining it from scratch. In this paper, we propose a novel efficient unlearning framework based on Optimal Transport, which can effectively work on class and instance-wise unlearning tasks. By analyzing and comparing the feature spaces of the original and retrained models, we formulate the unlearning problem as a distribution alignment task between the forget set and the retain set. We guide the feature distribution of the forget set, which initially forms distinct, structured patterns, to align with that of the retain set. In addition, we introduce a class-aware cost function for optimal transport that encourages inter-class transport, thereby enhancing the forgetting process. Extensive experiments on three public benchmark datasets demonstrate its superior effectiveness compared to previous SOTA methods."
    },
    {
        "title": "Beyond Masking: Landmark-based Representation Learning and Knowledge-Distillation for Audio-Visual Deepfake Detection",
        "authors": [
            "Chan Park",
            "Muhammad Shahid Muneer",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/2025_CIKM_Chan.png",
        "abstract": "Audio-visual deepfake detection methods demonstrate strong performance on academic datasets but fail significantly when applied to real-world deepfake content. To address the shortcomings of previous approaches, we introduce a landmark-guided knowledge-distillation framework, featuring two core innovations that enable the effective detection of real-world deepfakes. First, we propose Landmark-based Distillation (LBD), motivated by I-JEPA's representation learning approach. LBD utilizes KL-divergence to align facial landmark predictions from visual and audio encoders, enforcing focus on geometric facial features rather than spurious background information. Second, we introduce Multimodal Temporal Information Alignment (MTIA), which employs contrastive learning to enhance temporal consistency between audio and visual representations. We conduct extensive experiments on academic datasets and web-based deepfakes collected from diverse social media platforms, serving as real-world examples. Our proposed landmark-guided distillation framework achieves computational efficiency while improving multimodal video deepfake detection performance across a diverse range of deepfakes compared to existing methods."
    },
    {
        "title": "Learning Interpersonal Similarities in Multiple Fingers via Fingerprint Landmark-Aware Recognition Network",
        "authors": [
            "Jiwon Kim",
            "Simon S. Woo",
            "Youjin Shin"
        ],
        "venue_full": "IEEE International Joint Conference on Biometrics",
        "venue": "IJCB",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            ">>Research Impact Score 1.90",
            0
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/IJCB_jiwon.png",
        "abstract": "In fingerprint biometric systems, fingerprint recognition traditionally focuses on identifying individuals based on the distinct fingerprints of different fingers, which is finger-specific identity recognition (FsIR). However, real-world applications often require recognizing the same individual using fingerprints from different fingers, which is finger-agnostic identity recognition (FaIR). The FaIR task has proven challenging due to the prevailing assumption in the biometric field that there is no correlation between an individual’s different fingerprints. To address this issue, we propose a novel system, IP-Fing, which can learn the interpersonal similarity across the fingers. By using a pre-trained localization encoder to capture interpersonal fingerprint landmarks and the ArcFace marginal logit function, our IP-Fing recognition system can match a fingerprint query to all fingerprints of the same person while distinguishing them from others. We assess our method using comprehensive tests on two fingerprint datasets: our private fingerprint dataset, KORFing, which only has one sample per finger available, and the public fingerprint dataset, CASIA-v5, which has a few missing fingerprint samples for the task of finger-agnostic identity recognition (FaIR). IP-Fing achieves the best AUC with an average of 95.3074 across the two datasets, showing that our method is more effective in applying FaIR than conventional methods. Furthermore, IP-Fing demonstrates superior AUC with an average of 98.4631 across two datasets in the task of traditional finger-specific identity recognition (FsIR)."
    },
    {
        "title": "From Prediction to Explanation: Multimodal, Explainable, and Interactive Deepfake Detection Framework for Non-Expert Users",
        "authors": [
            "Shahroz Tariq",
            "PRIYANKA SINGH",
            "Simon S. Woo",
            "Irena Irmalasari",
            "Saakshi Gupta",
            "Dev Gupta"
        ],
        "venue_full": "ACM International Conference on Multimedia",
        "venue": "MM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/Sharoz.png",
        "abstract": "The proliferation of deepfake technologies poses urgent challenges and serious risks to digital integrity, particularly within critical sectors such as forensics, journalism, and the legal system. While existing detection systems have made significant progress in classification accuracy, they typically function as black-box models—offering limited transparency and minimal support for human reasoning. This lack of interpretability hinders their usability in real-world decision-making contexts, especially for non-expert users. In this paper, we present DF-P2E (Deepfake: Prediction to Explanation), a novel multimodal framework that integrates visual, semantic, and narrative layers of explanation to make deepfake detection interpretable and accessible. The framework consists of three modular components: (1) a deepfake classifier with Grad-CAM-based saliency visualisation, (2) a visual captioning module that generates natural language summaries of manipulated regions, and (3) a narrative refinement module that uses a fine-tuned Large Language Model (LLM) to produce context-aware, user-sensitive explanations. We instantiate and evaluate the framework on the DF40 benchmark, the most diverse deepfake dataset to date. Experiments demonstrate that our system achieves competitive detection performance while providing high-quality explanations aligned with Grad-CAM activations. Human evaluation with non-expert participants confirms the perceived usefulness, understandability, and trustworthiness of the generated narratives. By unifying prediction and explanation in a coherent, human-aligned pipeline, this work offers a scalable approach to interpretable deepfake detection—advancing the broader vision of trustworthy and transparent AI systems in adversarial media environments."
    },
    {
        "title": "PromptFlare: Prompt-Generalized Defense via Cross-Attention Decoy in Diffusion-Based Inpainting",
        "authors": [
            "Hohyun Na",
            "Seunghoo Hong",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Multimedia",
        "venue": "MM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/figure2.png",
        "abstract": "The success of diffusion models has enabled effortless, high-quality image modifications that precisely align with users' intentions, thereby raising concerns about their potential misuse by malicious actors. Previous studies have attempted to mitigate such misuse through adversarial attacks. However, these approaches heavily rely on image-level inconsistencies, which pose fundamental limitations in addressing the influence of textual prompts. In this paper, we propose PromptFlare, a novel adversarial protection method designed to protect images from malicious modifications facilitated by diffusion-based inpainting models. Our approach leverages the cross-attention mechanism to exploit the intrinsic properties of prompt embeddings. Specifically, we identify and target shared token of prompts that are invariant and semantically uninformative, injecting adversarial noise to suppress the sampling process. Extensive experiments on the EditBench dataset demonstrate that our method achieves state-of-the-art performance across various CLIP-based and traditional metrics while significantly reducing computational overhead and GPU memory usage. These findings highlight PromptFlare as a robust and efficient protection against unauthorized image manipulations."
    },
    {
        "title": "SpecXNet: A Dual-Domain Convolutional Network for Robust Deepfake Detection",
        "authors": [
            "Inzamamul Alam",
            "Md Tanvir Islam",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Multimedia",
        "venue": "MM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/high-level-dig.jpg",
        "abstract": "The increasing realism of content generated by GANs and diffusion models has made deepfake detection significantly more challenging. Existing approaches often focus solely on spatial or frequency-domain features, limiting their generalization to unseen manipulations. We propose the Spectral Cross-Attentional Network (SpecXNet), a dual-domain architecture for robust deepfake detection. The core \\textbf{Dual-Domain Feature Coupler (DDFC)} decomposes features into a local spatial branch for capturing texture-level anomalies and a global spectral branch that employs Fast Fourier Transform to model periodic inconsistencies. This dual-domain formulation allows SpecXNet to jointly exploit localized detail and global structural coherence, which are critical for distinguishing authentic from manipulated images. We also introduce the \\textbf{Dual Fourier Attention (DFA)} module, which dynamically fuses spatial and spectral features in a content-aware manner. Built atop a modified XceptionNet backbone, we embed the DDFC and DFA modules within a separable convolution block. Extensive experiments on multiple deepfake benchmarks show that SpecXNet achieves state-of-the-art accuracy, particularly under cross-dataset and unseen manipulation scenarios, while maintaining real-time feasibility. Our results highlight the effectiveness of unified spatial-spectral learning for robust and generalizable deepfake detection."
    },
    {
        "title": "Combating Dataset Misalignment for Robust AI-Generated Image Detection in the Real World",
        "authors": [
            "Hyeongjun Choi",
            "Inho Jung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3709022.3736541"
        },
        "img": "/img/Publications/WDC25.png",
        "abstract": "AI-generated images are increasingly prevalent on the web, raising concerns about the real-world applicability of detection methods. While current detectors perform well on benchmark datasets, they suffer significant performance degradation on real-world datasets. Misalignment within benchmark datasets, caused by discrepancies in how data from different classes are encoded or transformed, leads models to learn shortcuts. These shortcuts make detectors overly reliant on factors such as image compression, causing biased predictions of real-world images that inevitably undergo compression. In this work, we reveal the misalignment in widely used benchmark datasets and demonstrate that aligning datasets improves model robustness and generalizability. Additionally, we propose leveraging pre-trained visual encoders to further enhance performance in real-world scenarios. Our approach achieves significant performance gains, highlighting the importance of dataset alignment for real-world AI-generated image detection."
    },
    {
        "title": "DIA: The Adversarial Exposure of Deterministic Inversion in Diffusion Models",
        "authors": [
            "Seunghoo Hong",
            "Geonho Son",
            "Juhun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Computer Vision",
        "venue": "ICCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2510.00778"
        },
        "img": "/img/Publications/DIA-ICCV2025.png",
        "abstract": "Diffusion models have shown to be strong representation learners, showcasing state-of-the-art performance across multiple domains. Aside from accelerated sampling, DDIM also enables the inversion of real images back to their latent codes. A direct inheriting application of this inversion operation is real image editing, where the inversion yields latent trajectories to be utilized during the synthesis of the edited image. Unfortunately, this practical tool has enabled malicious users to freely synthesize misinformative or deepfake contents with greater ease, which promotes the spread of unethical and abusive, as well as privacy-, and copyright-infringing contents. While defensive algorithms such as AdvDM and Photoguard have been shown to disrupt the diffusion process on these images, the misalignment between their objectives and the iterative denoising trajectory at test time results in weak disruptive performance.In this work, we present the DDIM Inversion Attack (DIA) that attacks the integrated DDIM trajectory path. Our results support the effective disruption, surpassing previous defensive methods across various editing methods. We believe that our frameworks and results can provide practical defense methods against the malicious use of AI for both the industry and the research community."
    },
    {
        "title": "Translation of Text Embedding via Delta Vector to Suppress Strongly Entangled Content in Text-to-Image Diffusion Models",
        "authors": [
            "Seunghoo Hong†",
            "Eunseo Koh†",
            "Tae-Young Kim†",
            "Jae-Pil Heo",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Computer Vision",
        "venue": "ICCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/SSDV.png",
        "abstract": "Text-to-Image (T2I) diffusion models have made significant progress in generating diverse high-quality images from textual prompts. However, these models still face challenges in suppressing content that is strongly entangled with specific words. For example, when generating an image of \"Charlie Chaplin\", a \"mustache\" consistently appears even if explicitly instructed not to include it, as the concept of \"mustache\" is strongly entangled with \"Charlie Chaplin\". To address this issue, we propose a novel approach to directly suppress such entangled content within the text embedding space of diffusion models. Our method introduces a delta vector that modifies the text embedding to weaken the influence of undesired content in the generated image, and we further demonstrate that this delta vector can be easily obtained through a zero-shot approach. Furthermore, we propose a Selective Suppression with Delta Vector (SSDV) method to adapt the delta vector into the cross-attention mechanism, enabling more effective suppression of unwanted content in regions where it would otherwise be generated. Additionally, we enabled more precise suppression in personalized T2I models by optimizing the delta vector, which previous baselines were unable to achieve. Extensive experimental results demonstrate that our approach significantly outperforms existing methods, both in terms of quantitative and qualitative metrics."
    },
    {
        "title": "SpecGuard: Spectral Projection-based Advanced InvisibleWatermarking",
        "authors": [
            "Inzamamul Alam",
            "Md Tanvir Islam",
            "Khan Muhammad",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Computer Vision",
        "venue": "ICCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/ProposedModel-01.jpg",
        "abstract": "Watermarking embeds imperceptible patterns into images for authenticity verification. However, existing methods often lack robustness against various transformations primar ily including distortions, image regeneration, and adver sarial perturbation, creating real-world challenges. In this work, we introduce SpecGuard, a novel watermarking ap proach for robust and invisible image watermarking. Un like prior approaches, we embed the message inside hid den convolution layers by converting from the spatial do main to the frequency domain using spectral projection of a higher frequency band that is decomposed by wavelet pro jection. Spectral projection employs Fast Fourier Trans form approximation to transform spatial data into the fre quency domain efficiently. In the encoding phase, a strength factor enhances resilience against diverse attacks, includ ing adversarial, geometric, and regeneration-based distor tions, ensuring the preservation of copyrighted information. Meanwhile, the decoder leverages Parseval’s theorem to ef fectively learn and extract the watermark pattern, enabling accurate retrieval under challenging transformations. We evaluate the proposed SpecGuard based on the embedded watermark’s invisibility, capacity, and robustness. Compre hensive experiments demonstrate the proposed SpecGuard outperforms the state-of-the-art models."
    },
    {
        "title": "HiDF: A Human-Indistinguishable Deepfake Dataset",
        "authors": [
            "Chaewon Kang",
            "Seoyoon Jeong",
            "Jonghyun Lee",
            "Daejin Choi",
            "Simon S. Woo",
            "Jinyoung Han"
        ],
        "venue_full": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "venue": "KDD",
        "track": "Dataset Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3711896.3737399"
        },
        "img": "/img/Publications/KDD2025_HiDF.png",
        "abstract": "The rapid development and prevalence of generative AI have made it easy for people to create high-quality deepfake images and videos, but their abuses have also increased exponentially. To mitigate potential social disruption, it is crucial to quickly detect the authenticity of each deepfake content hidden in a sea of information. While researchers have worked on developing deep learning-based methods, the deepfake datasets utilized in these studies are far from the real world in terms of their qualities; most popular deepfake datasets are human-distinguishable. To address this problem, we present a novel deepfake dataset, HiDF, a high-quality and humanindistinguishable deepfake dataset consisting of 62 K images and 8 K videos. HiDF is a meticulously curated dataset that includes diverse subjects that have undergone rigorous quality checks. A comparison of the quality between HiDF and existing deepfake datasets demonstrates that HiDF is human-indistinguishable. Hence, it can be a valuable benchmark dataset for deepfake detection tasks."
    },
    {
        "title": "SEE: Spherical Embedding Expansion for Improving Deep Metric Learning (Extended Abstract)",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "International Joint Conference on Artificial Intelligence",
        "venue": "IJCAI",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.24963/ijcai.2024/1214"
        },
        "img": "/img/Publications/binhle_pakdd2024.png",
        "abstract": "We introduce the Spherical Embedding Expansion (SEE) method. SEE aims to uncover the latent semantic variations in training data. Especially, our method augments the embedding space with synthetic representations based on Max-Mahalanobis distribution (MMD) centers, which maximize the dispersion of these synthetic features without increasing computational costs.We evaluated the efficacy of SEE on four renowned standard benchmarks for the image retrieval task. The results demonstrate that SEE consistently enhances the performance of conventional methods when integrated with them, setting a new benchmark for deep metric learning performance across all settings."
    },
    {
        "title": "Toward a robust approach to multivariate time series anomaly detection",
        "authors": [
            "Jungwook Shon",
            "Simon S. Woo"
        ],
        "venue_full": "Metrology, Inspection, and Process Control XXXIX",
        "venue": "JM3",
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            1.5
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1117/12.3050401"
        },
        "img": "/img/Publications/SPIE_jw.png",
        "abstract": "Anomaly detection in semiconductor manufacturing is critical for maintaining yield and reducing costs, especially in high-volume production environments where inspections are resource-intensive. This study presents a robust, unsupervised deep learning framework for multivariate anomaly detection that addresses limitations of existing Fault Detection and Classification (FDC) systems. The proposed approach leverages a Transformer-based model enhanced with Aggregated z-normalization to mitigate distribution drift, and employs Peaks-Over-Threshold (POT) for adaptive thresholding. The framework achieved an F1 score of 0.9827 and a precision of 0.9866 on semiconductor datasets, with minimal false alarms validated through extensive ablation studies. The solution is designed for scalability and adaptability in industrial settings, with future work focused on improving detection of single-spike anomalies and borderline cases to enhance operational reliability."
    },
    {
        "title": "Self-Disclosure of Mental Health via Deepfakes: Testing the Effects of Self-Deepfakes on Affective Resistance and Intentions to Seek Mental Health Support",
        "authors": [
            "Jiyoung Lee",
            "Christopher Michael Dobmeier",
            "Minji Heo",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Computational Social Science",
        "venue": "IC2S2",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {},
        "img": "/img/Publications/self_disclosure.png",
        "abstract": "Theoretically, the current study revisits traditional video self-modeling approaches, which leverage the self-referencing effect to enhance engagement, within the context of deepfake technology by integrating the self-referencing effect and the uncanny valley effect. This study reveals that the synthesized nature of self-representations in deepfakes introduces artificiality that triggers discomfort, thereby increasing resistance to mental health self-disclosure messages. This discomfort underscores a significant limitation of deepfake technology in sensitive contexts, as individuals—especially those with higher baseline levels of mental health who find greater relevance to the topic—may be reluctant to engage with messages that present uncanny or distorted self-representations. Our findings emphasize the importance of future research to systematically investigate the boundaries of self-referencing in AI-driven synthetic media, focusing on how the degree of resemblance influences perceptions of personal relevance, evokes emotional resistance, and varies across individual differences. Furthermore, as deepfake technology finds its way into the healthcare sector, practitioners must remain mindful that while it offers innovative possibilities, it may also stir emotional resistance."
    },
    {
        "title": "SoK: Systematization and Benchmarking of Deepfake Detectors in a Unified Framework",
        "authors": [
            "Binh M. Le",
            "Jiwon Kim",
            "Simon S. Woo",
            "Kristen Moore",
            "Alsharif Abuadbba",
            "Shahroz Tariq"
        ],
        "venue_full": "IEEE European Symposium on Security and Privacy",
        "venue": "EuroS&P",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1109/eurosp63326.2025.00055"
        },
        "img": "/img/Publications/2025_EuroS&P.png",
        "abstract": "This paper extensively reviews and analyzes state-of-the-art deepfake detectors, evaluating them against several critical criteria. These criteria categorize detectors into 4 high-level groups and 13 fine-grained sub-groups, aligned with a unified conceptual framework we propose. This classification offers practical insights into the factors affecting detector efficacy. We evaluate the generalizability of 16 leading detectors across comprehensive attack scenarios, including black-box, white-box, and gray-box settings. Our systematized analysis and experiments provide a deeper understanding of deepfake detectors and their generalizability, paving the way for future research and the development of more proactive defenses against deepfakes."
    },
    {
        "title": "Towards Safe Synthetic Image Generation On the Web: A Multimodal Robust NSFW Defense and Million Scale Dataset",
        "authors": [
            "Muhammad Shahid Muneer",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3701716.3715526"
        },
        "img": "/img/Publications/WWW2025_shahid.jpg",
        "abstract": "Defensive mechanisms such as NSFW and post-hoc security filters are implemented in T2I models to mitigate the misuse of T2I models and develop a safe online ecosystem for web users. However, recent work unveiled how these methods can easily fail to prevent misuse. In particular, careful adversarial attacks on text and image modalities can easily outplay defensive measures. Moreover, there is no robust millionscale multimodal NSFW dataset with both prompt and image pairs with adversarial examples. In this work, we propose a large-scale prompt and image dataset, generated using open-source diffusion models. Also, we develop a multimodal classification model to distinguish safe and NSFW text and images, which has robustness against adversarial attacks, and directly alleviates the current challenges. Our extensive experimental results show that our model shows good performance against existing SOTA NSFW detection methods in terms of accuracy and recall, and drastically reduced the Attack Success Rate (ASR) in multimodal adversarial attack scenarios."
    },
    {
        "title": "Fairness and Robustness in Machine Unlearning",
        "authors": [
            "Khoa Tran",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3701716.3715598"
        },
        "img": "/img/Publications/WWW2025_khoa.png",
        "abstract": "Our study presents fairness Conjectures for a well-trained model, based on the variance-bias trade-off characteristic, and considers their relevance to robustness. Our Conjectures are supported by experiments conducted on the two most widely used model architectures—ResNet and ViT—demonstrating the correlation between fairness and robustness: the higher fairness-gap is, the more the model is sensitive and vulnerable. In addition, our experiments demonstrate the vulnerability of current state-of-the-art approximated unlearning algorithms to adversarial attacks, where their unlearned models suffer a significant drop in accuracy compared  to the exact-unlearned models.We claim that our fairness-gap measurement and robustness metric should be used to evaluate the unlearning algorithm. Furthermore, we demonstrate that unlearning in the intermediate and last layers is sufficient and cost-effective for time and memory complexity."
    },
    {
        "title": "Saliency-Aware Diffusion Reconstruction for Effective Invisible Watermark Removal",
        "authors": [
            "Inzamamul Alam",
            "Md Tanvir Islam",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3701716.3715519"
        },
        "img": "/img/Publications/WWW2025_inzi.png",
        "abstract": "This paper introduces a novel Saliency-Aware Diffusion Reconstruction (SADRE) framework for watermark elimination on the web, combining adaptive noise injection, region-specific perturbations, and advanced diffusion-based reconstruction. SADRE disrupts embedded watermarks by injecting targeted noise into latent representations guided by saliency masks although preserving essential image features. A reverse diffusion process ensures high-fidelity image restoration, leveraging adaptive noise levels determined by watermark strength. Our framework is theoretically grounded with stability guarantees and achieves robust watermark removal across diverse scenarios. Empirical evaluations on state-of-the-art (SOTA) watermarking techniques demonstrate SADRE’s superiority in balancing watermark disruption and image quality, achieving the best performance in PSNR, SSIM, Wasserstein Distance, and Bit Recovery Accuracy. By bridging the gap between theoretical robustness and practical effectiveness, SADRE sets a new benchmark for watermark elimination, offering a flexible and reliable solution for real-world web contents."
    },
    {
        "title": "GAN or DM? In-depth Analysis and Evaluation of AI-generated Face Data for Generalizable Deepfake Detection",
        "authors": [
            "Hyeongjun Choi",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3672608.3707733"
        },
        "img": "/img/Publications/SAC_hyeongjun.jpg",
        "abstract": "In this work, we train popular deep neural networks using face data generated by various generative models and thoroughly analyze their generalizability. Our results reveal significant differences in model performance based on the forgery method used to generate the training data. Notably, we identify specific scenarios that significantly enhance model generalization, contradicting previous research finding that models trained on DM-generated data would achieve higher generalization performance than those trained on GAN-generated data. These findings emphasize the crucial role of training data selection in enhancing the generalization capabilities of deepfake detectors. By strategically selecting and combining datasets, we can develop more robust detection systems, laying a foundation for future research in creating reliable and universal deepfake detection methods"
    },
    {
        "title": "X3A: Efficient Multimodal Deepfake Detection with Score-Level Fusion",
        "authors": [
            "Chan Park",
            "Bohyun Moon",
            "Minsun Jeon",
            "Jee-weon Jung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3672608.3707934"
        },
        "img": "/img/Publications/Park_SCD_2025.png",
        "abstract": "In this work, we propose X3A, an efficient multimodal video deepfake detection model exploiting two powerful unimodal models with probabilistic score-level fusion. X3A leverages the advantage of using raw visual and audio inputs without relying on hand-crafted features. We conducted the extensive experiments on multiple different multimodal deepfake benchmark datasets and achieved superior performance on multimodal deepfake detection, successively detecting entirely and partially manipulated scenarios. Our X3A model demonstrates an accuracy of 0.9960 AUC of 0.9999 on the most challenging AVDeepfake1M benchmark, surpassing all existing models."
    },
    {
        "title": "High-Fidelity Face Age Transformation via Hierarchical Encoding and Contrastive Learning",
        "authors": [
            "Hakjun Moon",
            "Dayeon Woo",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1145/3672608.3707795"
        },
        "img": "/img/Publications/Moon_SCD_2025.png",
        "abstract": "We introduce a novel GAN-based face age transformation framework utilizing Hierarchical Encoding and Contrastive Learning (HECL). Specifically, we incorporate a multi-level encoder that extracts and analyzes age-related features at different levels of detail, such as facial texture, structure, and skin tone.\n We also combined a contrastive learning approach in the discriminator to finetune the differentiation between age groups. These modifications enhance identity preservation and provide better control over aging through strategic loss functions, addressing shortcomings in existing models, which often struggle with modifying subtle face and hair texture, color, or volume during age progression. HECL outperforms SOTA models in realism and versatility, generating high-quality face images. We demonstrate superior identity preservation performance in metrics, also receiving better qualitative approval from human evaluators."
    },
    {
        "title": "Development of Deep Learning-Based Algorithm for Extracting Abnormal Deceleration Patterns",
        "authors": [
            "Youngho Jun",
            "Minha Kim",
            "Kangjun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "World Electric Vehicle Journal",
        "venue": "WEVJ",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            2.6
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.3390/wevj16010037"
        },
        "img": "/img/Publications/Jun_WEVJ_2025.png",
        "abstract": "The smart regenerative braking system for EV can reduce unnecessary brake operation by assisting in braking of the vehicle according to the driving situation, road slope, and driver’s preference. This system maintains the distance between the ego and front vehicles without controlling the brake pedal. Since the strength of regenerative braking is generally determined based on calibration data determined during the vehicle development process, some driver could suffer inconvenience when the regenerative braking is activated differently from their driving habits. In order to solve this problem, various deep learning-based algorithms are developed to provide driving stability by learning the driving data. Among those artificial intelligence algorithms, anomaly detection algorithms can successfully separate the deceleration data in abnormal driving situations, and the resulting refined deceleration data can be used to train the regression model to achieve better driving stability. This study evaluates the performance of a personalized driving assistance system by applying driver characteristic data, obtained through an anomaly detection algorithm, to vehicle control."
    },
    {
        "title": "MIRACLE: Malware image recognition and classification by layered extraction",
        "authors": [
            "Inzamamul Alam",
            "Md. Samiullah",
            "S M Asaduzzaman",
            "Upama Kabir",
            "A. M. Aahad",
            "Simon S. Woo"
        ],
        "venue_full": "Data Mining and Knowledge Discovery",
        "venue": "DMKD",
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            5.3
        ],
        "year": 2025,
        "links": {
            "conf": "https://doi.org/10.1007/s10618-024-01078-z"
        },
        "img": "/img/Publications/DMKD_Figure_1.png",
        "abstract": "We propose a novel approach, Malware Image Recognition & Classification by Layered Extraction (MIRACLE), by implementing our own spatial convolutional neural network (Sp-CNN) with sufficient regularization and data augmentation to identify and classify malware in images effectively and efficiently. Our proposed method is developed based on analyzing malware binary structure, which is segmented as headers and section, symbolic information lies on section segment. Our Sp-CNN can extract that symbolic information from the top of the hidden layer constructively. We have evaluated our model with as MalImg, Microfsoft-Big, Malevis and Android Malware dataset. We achieved accuracy of 99.87% for MalImg, 99.81% for Microsoft-Big, and 99.22% for Malevis in our test dataset, respectively. Our proposed method surpasses Google's InceptionV3, ResNet50, EfficientNetB1, VGG16, VGG19, and other state-of-the-art (SOTA) methods in terms of performance."
    },
    {
        "title": "Synthetic Data Generation Research Trends",
        "authors": [
            "Minsun Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Winter",
        "venue": "CISC-W",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {},
        "img": "/img/Publications/minsun_saftey_2.png",
        "abstract": "With the growing need to simultaneously address privacy protection and data utilization, synthetic data, a powerful anonymization technique, is gaining attention. This paper examines the types of synthetic data, key generation methods for different target subjects, and various application cases. Through this exploration, we aim to provide a more detailed understanding of synthetic data's advantages and potential applications, as well as insights into future research directions for expanding its use."
    },
    {
        "title": "Prioritizing Safety: A Two-Stage Not Safe For Work and Deepfake Detection Framework",
        "authors": [
            "Minsun Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Korean Artificial Intelligence Association",
        "venue": "KAIA",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {},
        "img": "/img/Publications/minsun_Safety.png",
        "abstract": "Deepfake content is being created automatically in large quantities, but it must still be reported manually by victims, making rapid responses difficult. Despite the prevalence of sexually exploitative deepfake, no existing approach has combined Not Safe For Work (NSFW) detection with deepfake detection. To address this issue, this study proposes a novel integrated process that first implements NSFW detection to assess urgency and identify sexual components before proceeding to deepfake detection. To verify the effectiveness of this process, we generated eight FaceSwap images. In addition, we utilized these images to evaluate the performance of the NSFW and deepfake detection models, achieving an accuracy of 87.5% and 100%, respectively. The results demonstrated the viability of a sequential detection approach. This research highlights the importance of combining NSFW and deepfake detection for more efficient and urgent content moderation, providing a practical tool for law enforcement and victim support organizations. In our findings, this research presents a paradigm that enables rapid responses to address the harms caused by deepfake content effectively and promotes a more proactive approach to content moderation."
    },
    {
        "title": "An Empirical Study of Black-Box Based Membership Inference Attacks on a Real-World Dataset",
        "authors": [
            "Yujeong Kwon",
            "Simon S. Woo",
            "Hyungjoon Koo"
        ],
        "venue_full": "International Symposium on Foundations and Practice of Security",
        "venue": "FPS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-87496-3_9"
        },
        "img": "/img/Publications/membership_attack.png",
        "abstract": "The recent advancements in artificial intelligence drive the widespread adoption of Machine-Learning-as-a-Service platforms, which offer valuable services. However, these pervasive utilities in the cloud environment unavoidably encounter security and privacy issues. In particular, a membership inference attack (MIA) poses a threat by recognizing the presence of a data sample in a training set for the target model. Although prior MIA approaches underline privacy risks repeatedly by demonstrating experimental results with standard benchmark datasets such as MNIST and CIFAR, the effectiveness of such techniques on a real-world dataset remains questionable. We are the first to perform an in-depth empirical study on black-box-based MIAs that hold realistic assumptions, including six metric-based and three classifier-based MIAs with the high-dimensional image dataset that consists of identification (ID) cards and driving licenses. Additionally, we introduce the Siamese-based MIA that shows similar or better performance than the state-of-the-art approaches and suggest training a shadow model with autoencoder-based reconstructed images. Our major findings show that the performance of MIA techniques against too many features may be degraded; the MIA configuration or a sample's properties can impact the accuracy of membership inference on members and non-members."
    },
    {
        "title": "LoLI-Street: Benchmarking Low-Light Image Enhancement and Beyond",
        "authors": [
            "Md Tanvir Islam",
            "Inzamamul Alam",
            "Simon S. Woo",
            "Saeed Anwar",
            "Ik Hyun Lee",
            "Khan Muhammad"
        ],
        "venue_full": "Asian Conference on Computer Vision",
        "venue": "ACCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-96-0917-8_20"
        },
        "img": "/img/Publications/ACCV-2024-2.png",
        "abstract": "We introduce a new large-scale dataset “LoLI-Street” (Low-Light Images of Streets) with 33k paired low-light and well-exposed images from street scenes in developed cities, covering 19k object classes for object detection, including Person, Bicycle, Car, Bus, Motorcycle, and Traffic Light, etc. LoLI-Street dataset also features 1,000 real low-light test images, providing a benchmark for evaluating models under real-world conditions. Furthermore, we propose a transformer and diffusion-based LLIE model named “TriFuse”. Leveraging the LoLI-Street dataset, we train and evaluate our TriFuse and other SOTA models to benchmark our dataset. Comparing various models, the feasibility of our dataset for generalization is evident in testing across different mainstream datasets by significantly enhancing low-quality images and object detection for practical applications in autonomous driving and surveillance systems. The benchmark dataset and the evaluation code will be released to ensure reproducibility."
    },
    {
        "title": "Bridging Optimal Transport and Jacobian Regularization by Optimal Trajectory for Enhanced Adversarial Defense",
        "authors": [
            "Binh M. Le",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "Asian Conference on Computer Vision",
        "venue": "ACCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-96-0963-5_7"
        },
        "img": "/img/Publications/ACCV-2024-1.png",
        "abstract": "Deep neural networks, particularly in vision tasks, are notably susceptible to adversarial perturbations. To overcome this chal lenge, developing a robust classifier is crucial. In light of the recent advancements in the robustness of classifiers, we delve deep into the intricacies of adversarial training and Jacobian regularization, two pivotal defenses. Our work is the first carefully analyzes and characterizes these two schools of approaches, both theoretically and empirically, to demonstrate how each approach impacts the robust learning of a classifier. Next, we propose our novel Optimal Transport with Jacobian regularization  method, dubbed OTJR, bridging the input Jacobian regularization with the a output representation alignment by leveraging the optimal transport theory. In particular, we employ the Sliced Wasserstein distance that can efficiently push the adversarial samples’ representations closer to those of clean samples, regardless of the number of classes within the dataset. The SW distance provides the adversarial samples’ movement directions, which are much more informative and powerful for the Jacobian regularization. Our empirical evaluations set a new standard in the domain, with our method achieving commendable accuracies of 52.57% on CIFAR-10 and 28.36% on CIFAR-100 datasets under the AutoAttack. Further validating our model’s practicality, we conducted real-world tests by subjecting internet-sourced images to online adversarial attacks. These demonstrations highlight our model’s capability to counteract sophisticated adversarial perturbations, affirming its significance and applicability in real-world scenarios."
    },
    {
        "title": "Adaptive Clustering and Step-Size Optimization in Collaborative Distributed Diffusion-Based AIGC: Balancing Performance and Resource Utilization",
        "authors": [
            "Zeliang Xu",
            "Dong In Kim",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Information and Communication Technology Convergence",
        "venue": "ICTC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/ictc62082.2024.10826855"
        },
        "img": "/img/Publications/ICTC 2024.png",
        "abstract": "This paper proposes a novel cloud-edge collaborative distributed diffusion model for AI-generated content (AIGC) such as image generation, which integrates adaptive clustering techniques with dynamic step-size optimization. The proposed model addresses the challenges of heterogeneous edge devices in real-world deployments. Experimental results demonstrate significant improvements in performance and efficiency with\na 38.8% reduction in average generation time and a 15.6% increase in image quality (evaluate via CLIP score). The system shows enhanced resource utilization, improving cloud and edge utilization by 16.1% and 36.6%, respectively. This research contributes to the advancement of collaborative distributed diffusion model, offering a scalable and adaptive framework for efficient\nAIGC services in dynamic environments along with potential applications extending to other computationally intensive tasks in cloud-edge systems."
    },
    {
        "title": "A real-world pharmacovigilance study on cardiovascular adverse events of tisagenlecleucel using machine learning approach",
        "authors": [
            "Juhong Jung",
            "Ju Hwan Kim",
            "Ji-Hwan Bae",
            "Simon S. Woo",
            "Hyesung Lee",
            "Ju-Young Shin"
        ],
        "venue_full": "Scientific Reports",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF=",
            3.9
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1038/s41598-024-64466-x"
        },
        "img": "/img/Publications/nature-2024.webp",
        "abstract": "In this study, gradient boosting machine algorithm-based model was fitted to identify safety signals of serious cardiovascular AEs reported for tisagenlecleucel in the World Health Organization Vigibase up until February 2024. Input dataset, comprised of positive and negative controls of tisagenlecleucel based on its labeling information and literature search, was used to train the model. Then, we implemented the model to calculate the predicted probability of serious cardiovascular AEs defined by preferred terms included in the important medical event list from European Medicine Agency. There were 467 distinct AEs from 3,280 safety cases reports for tisagenlecleucel, of which 363 (77.7%) were classified as positive controls, 66 (14.2%) as negative controls, and 37 (7.9%) as unknown AEs. The prediction model had area under the receiver operating characteristic curve of 0.76 in the test dataset application. Of the unknown AEs, six cardiovascular AEs were predicted as the safety signals: bradycardia (predicted probability 0.99), pleural effusion (0.98), pulseless electrical activity (0.89), cardiotoxicity (0.83), cardio-respiratory arrest (0.69), and acute myocardial infarction (0.58). Our findings underscore vigilant monitoring of acute cardiotoxicities with tisagenlecleucel therapy."
    },
    {
        "title": "Satellite State Prediction and Maneuver Detection Analysis Using NCDEs",
        "authors": [
            "Kangjun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Pattern Recognition",
        "venue": "ICPR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-78189-6_15"
        },
        "img": "/img/Publications/kari.png",
        "abstract": "Satellite orbit propagation (SOP) are of prime importance in the prevention of collision and completion of the assigned task of the satellites. In the past, orbit prediction and propagation have relied on physics-based mathematical model. However, as the number of satellites and their data increases, it is crucial to explore the data-driven orbit propagation based on the advanced machine learning methods. In this work, we propose a novel deep learning-based framework to forecast future satellite orbit states. The proposed framework employs a model based on Neural Controlled Differential Equations (NCDEs) to train orbit prediction models, and our approach captures features from past satellite state values at both fixed and dynamic time intervals. The experimental results on Korea Aerospace Research Institute (KARI)’s KOMPSAT-3 and 5 datasets demonstrate that the proposed framework outperforms the other eight data-driven baseline forecasting models."
    },
    {
        "title": "SSMT: Few-Shot Traffic Forecasting with Single Source Meta-transfer Learning",
        "authors": [
            "Kishor Kumar Bhaumik",
            "Minha Kim",
            "Fahim Faisal Niloy",
            "Amin Ahsan Ali",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Pattern Recognition",
        "venue": "ICPR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-78195-7_4"
        },
        "img": "/img/Publications/ssmt.png",
        "abstract": "Traffic forecasting in Intelligent Transportation Systems (ITS) is vital for intelligent traffic prediction. Yet, ITS often relies on data from traffic sensors or vehicle devices, where certain cities might not have all those smart devices or enabling infrastructures. Also, recent studies have employed meta-learning to generalize spatial-temporal traffic networks, utilizing data from multiple cities for effective traffic forecasting for data-scarce target cities. However, collecting data from multiple cities can be costly and time-consuming. To tackle this challenge, we introduce Single Source Meta-Transfer Learning (SSMT ) which relies only on a single source city for traffic prediction. Our method harnesses this transferred knowledge to enable few-shot traffic forecasting, particularly when the target city possesses limited data. Specifically, we use memory-augmented attention to store the heterogeneous spatial knowledge from the source city and selectively recall them for the data-scarce target city. We extend the idea of sinusoidal positional encoding to establish meta-learning tasks by leveraging diverse temporal traffic patterns from the source city. Moreover, to capture a more generalized representation of the positions we introduced a meta-positional encoding that learns the most optimal representation of the temporal pattern across all the tasks. We experiment on five real-world benchmark datasets to demonstrate that our method outperforms several existing methods in time series traffic prediction."
    },
    {
        "title": "MIXAD: Memory-Induced Explainable Time Series Anomaly Detection",
        "authors": [
            "Minha Kim",
            "Kishor Kumar Bhaumik",
            "Amin Ahsan Ali",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Pattern Recognition",
        "venue": "ICPR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-78189-6_16"
        },
        "img": "/img/Publications/mixad.png",
        "abstract": "For modern industrial applications, accurately detecting and diagnosing anomalies in multivariate time series data is essential. Despite this need, most state-of-the-art methods often prioritize detection performance over model interpretability. Addressing this gap, we introduce MIXAD (Memory-Induced Explainable Time Series Anomaly Detection), a model designed for interpretable anomaly detection. MIXAD leverages a memory network alongside spatiotemporal processing units to understand the intricate dynamics and topological structures inherent in sensor relationships. We also introduce a novel anomaly scoring method that detects significant shifts in memory activation patterns during anomalies. Our approach not only ensures decent detection performance but also outperforms state-of-the-art baselines by 34.30% and 34.51% in interpretability metrics."
    },
    {
        "title": "UGAD: Universal Generative AI Detector utilizing Frequency Fingerprints",
        "authors": [
            "Inzamamul Alam",
            "Muhammad Shahid Muneer",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3627673.3680085"
        },
        "img": "/img/Publications/cikm-inzi-2024.jpg",
        "abstract": "In the wake of a fabricated explosion image at the Pentagon, an ability to discern real images from fake counterparts has never been more critical. Our study introduces a novel multi-modal approach to detect AI-generated images amidst the proliferation of new generation methods such as Diffusion models. Our method, UGAD, encompasses three key detection steps: First, we transform the RGB images into YCbCr channels and apply an Integral Radial Operation to emphasize salient radial features. Secondly, the Spatial Fourier Extraction operation is used for a spatial shift, utilizing a pre-trained deep learning network for optimal feature extraction. Finally, the deep neural network classification stage processes the data through dense layers using softmax for classification. Our approach significantly enhances the accuracy of differentiating between real and AI-generated images, as evidenced by a 12.64% increase in accuracy and 28.43% increase in AUC compared to ex- isting state-of-the-art methods. Also, we integrated and deployed\n1 our approach to detect real-world deepfakes in our system."
    },
    {
        "title": "Blind-Match: Efficient Homomorphic Encryption-Based 1:N Matching for Privacy-Preserving Biometric Identification",
        "authors": [
            "Hyunmin Choi",
            "Jiwon Kim",
            "Chiyoung Song",
            "Simon S. Woo",
            "Hyoungshick Kim"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3627673.3680017"
        },
        "img": "/img/Publications/CIKM2024-choi.jpg",
        "abstract": "We present Blind-Match, a novel biometric identification system that leverages homomorphic encryption (HE) for efficient and privacy- preserving 1:N matching. Blind-Match introduces a HE-optimized cosine similarity computation method, where the key idea is to divide the feature vector into smaller parts for processing rather than comput- ing the entire vector at once. By optimizing the number of these parts, Blind-Match minimizes execution time while ensuring data privacy through HE. Blind-Match achieves superior performance compared to state-of-the-art methods across various biometric datasets. On the LFW face dataset, Blind-Match attains a 99.63% Rank-1 ac- curacy with a 128-dimensional feature vector, demonstrating its robustness in face recognition tasks. For fingerprint identification, Blind-Match achieves a remarkable 99.55% Rank-1 accuracy on the PolyU dataset, even with a compact 16-dimensional feature vector, significantly outperforming the state-of-the-art method, Blind-Touch, which achieves only 59.17%. Furthermore, Blind-Match showcases practical efficiency in large-scale biometric identification scenarios, such as Naver Cloud’s FaceSign, by processing 6,144 biometric samples in 0.74 seconds using a 128-dimensional feature vector."
    },
    {
        "title": "Deep Journey Hierarchical Attention Networks for Conversion Predictions in Digital Marketing",
        "authors": [
            "Girim Ban",
            "Hyeonseok Yun",
            "Banseok Lee",
            "David Sung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3627673.3680066"
        },
        "img": "/img/Publications/CIKM2024-ban.png",
        "abstract": "In digital marketing, precise audience targeting is crucial for campaign efficiency. However, digital marketing agencies often struggle with incomplete user profiles and interaction details from Advertising Identifier (ADID) data in user behavior modeling. To address this, Korea Telecom (KT), a leading telecommunication and big data service provider in South Korea, introduces the Deep Journey Hierarchical Attention Networks (DJHAN). This novel method enhances conversion predictions by leveraging heterogeneous action sequences associated with ADIDs and encapsulating these interactions into structured journeys. These journeys are hierarchically aggregated to effectively represent ADID’s behavioral attributes. Moreover, DJHAN incorporates three specialized attention mechanisms: temporal attention for time-sensitive contexts, action attention for emphasizing key behaviors, and journey attention for highlighting influential journeys in the purchase conversion process. Emprically, DJHAN surpasses state-of-the-art (SOTA) models across three diverse datasets, including real-world data from NasMedia, a leading media representative in Asia. In backtesting simulations with three advertisers, DJHAN outperforms existing baselines, achieving the highest improvements in Conversion Rate (CVR) and Return on Ad Spend (ROAS) across three advertisers, demonstrating its practical potential in digital marketing."
    },
    {
        "title": "Preserving Old Memories in Vivid Detail: Human-Interactive Photo Restoration Framework",
        "authors": [
            "Seung-Yeon Back",
            "Geonho Son",
            "Dahye Jeong",
            "Eunil Park",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3627673.3679215"
        },
        "img": "/img/Publications/CIKM2024-Back.jpg",
        "abstract": "Photo restoration technology enables preserving visual memories in photographs. However, physical prints are vulnerable to various forms of deterioration, ranging from physical damage to loss of image quality, etc. While restoration by human experts can improve the quality of outcomes, it often comes at a high price in terms of cost and time for restoration. In this work, we present the AI- based photo restoration framework composed of multiple stages, where each stage tailored to enhance and restore specific types of photo damage, accelerating and automating the photo restoration process. By integrating these techniques into a unified architecture, our framework aims to offer a one-stop solution for restoring old and deteriorated photographs. Furthermore, we present a novel old photo restoration dataset due to the lack of publicly available dataset for our evaulation."
    },
    {
        "title": "Continuous Memory Representation for Anomaly Detection",
        "authors": [
            "Joo Chan Lee",
            "Taejune Kim",
            "Eunbyung Park",
            "Simon S. Woo",
            "Jong Hwan Ko"
        ],
        "venue_full": "European Conference on Computer Vision",
        "venue": "ECCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-72983-6_25"
        },
        "img": "/img/Publications/eccv.png",
        "abstract": "There have been significant advancements in anomaly detection in an unsupervised manner, where only normal images are available for training. Several recent methods aim to detect anomalies based on a memory, comparing or reconstructing the input with directly stored normal features (or trained features with normal images). However, such memory-based approaches operate on a discrete feature space implemented by the nearest neighbor or attention mechanism, suffering from poor generalization or an identity shortcut issue outputting the same as input, respectively. Furthermore, the majority of existing methods are designed to detect single-class anomalies, resulting in unsatisfactory performance when presented with multiple classes of objects. To tackle all of the above challenges, we propose CRAD, a novel anomaly detection method for representing normal features within a “continuous” memory,enabled by transforming spatial features into coordinates and mapping them to continuous grids. Furthermore, we carefully design the grids tailored for anomaly detection, representing both local and global normal features and fusing them effectively. Our extensive experiments demonstrate that CRAD successfully generalizes the normal features and mitigates the identity shortcut, furthermore, CRAD effectively handles diverse classes in a single model thanks to the high-granularity continuous representation. In an evaluation using the MVTec AD dataset, CRAD significantly outperforms the previous state-of-the-art method by reducing 65.0% of the error for multi-class unified anomaly detection."
    },
    {
        "title": "Patch-wise vector quantization for unsupervised medical anomaly detection",
        "authors": [
            "Taejune Kim",
            "Yun-Gyoo Lee",
            "Inho Jeong",
            "Soo-Youn Ham",
            "Simon S. Woo"
        ],
        "venue_full": "Pattern Recognition Letters",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            5.1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1016/j.patrec.2024.06.028"
        },
        "img": "/img/Publications/prletters.png",
        "abstract": "Radiography images inherently possess globally consistent structures while exhibiting significant diversity in local anatomical regions, making it challenging to model their normal features through unsupervised anomaly detection. Since unsupervised anomaly detection methods localize anomalies by utilizing discrepancies between learned normal features and input abnormal features, previous studies introduce a memory structure to capture the normal features of radiography images. However, these approaches store extremely localized image segments in their memory, causing the model to represent both normal and pathological features with the stored components. This poses a significant challenge in unsupervised anomaly detection by reducing the disparity between learned features and abnormal features. Furthermore, with the diverse settings in radiography imaging, the above issue is exacerbated: more diversity in the normal images results in stronger representation of pathological features. To resolve the issues above, we propose a novel pathology detection method called Patch-wise Vector Quantization (P-VQ). Unlike the previous methods, P-VQ learns vector-quantized representations of normal \"patches\" while preserving its spatial information by incorporating vector similarity metric. Furthermore, we introduce a novel method for selecting features in the memory to further enhance the robustness against diverse imaging settings. P-VQ even mitigates the \"index collapse\" problem of vector quantization by proposing top-k% dropout. Our extensive experiments on the BMAD benchmark demonstrate the superior performance of P-VQ against existing state-of-the-art methods."
    },
    {
        "title": "Exploring the Impact of Moiré Pattern on Deepfake Detectors",
        "authors": [
            "Razaib Tariq",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Image Processing",
        "venue": "ICIP",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/icip51287.2024.10647902"
        },
        "img": "/img/Publications/ICIP_workshop.png",
        "abstract": "Deepfake detection is critical in mitigating the societal threats posed by manipulated videos. While various algorithms have been developed for this purpose, challenges arise when detectors operate externally, such as on smartphones, when users take a photo of deepfake images and upload on the Internet. One significant challenge in such scenarios is the presence of Moiré patterns, which degrade image quality and confound conventional classification algorithms, including deep neural networks (DNNs). The impact of Moiré patterns remains largely unexplored for deepfake detectors. In this study, we investigate how camera-captured deepfake videos from digital screens affect detector performance. We conducted experiments using two prominent datasets, CelebDF and FF++, comparing the performance of four state-of-the-art detectors on camera-captured deepfake videos with introduced Moiré patterns. Our findings reveal a significant decline in detector accuracy, with none achieving above 68% on average. This underscores the critical need to address Moiré pattern challenges in real-world deepfake detection scenarios."
    },
    {
        "title": "Decomposed Attention Segment Recurrent Neural Network for Orbit Prediction",
        "authors": [
            "SeungWon Jeong",
            "Soyeon Woo",
            "Daewon Chung",
            "Simon S. Woo",
            "Youjin Shin"
        ],
        "venue_full": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "venue": "KDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3637528.3671546"
        },
        "img": "/img/Publications/SIGKDD24.png",
        "abstract": "As the focus of space exploration shifts from national agencies to private companies, the interest in space industry has been steadily increasing. With the increasing number of satellites, the risk of collisions between satellites and space debris has escalated, potentially leading to significant property and human losses. Therefore,\naccurately modeling the orbit is critical for satellite operations. In this work, we propose the Decomposed Attention Segment Recurrent Neural Network (DASR) model, adding two key components, Multi-Head Attention and Tensor Train Decomposition, to SegRNN for orbit prediction. The DASR model applies Multi-Head Attention before segmenting at input data and before the input of the GRU layers. In addition, Tensor Train (TT) Decomposition is applied to the weight matrices of the Multi-Head Attention in both the encoder and decoder. For evaluation, we use three real-world satellite datasets from the Korea Aerospace Research Institute (KARI),\nwhich are currently operating: KOMPSAT-3, KOMPSAT-3A, and KOMPSAT-5 satellites. Our proposed model demonstrates superior performance compared to other SOTA baseline models. We demonstrate that our approach is 94.13% higher predictive performance than the second-best model in the KOMPSAT-3 dataset, 89.79% higher in the KOMPSAT-3A dataset, and 76.71% higher in the KOMPSAT-3 dataset."
    },
    {
        "title": "DynaPP: A Dynamic Resolution Model with Patch Packing for Fast Online Video Detection",
        "authors": [
            "Changrok So",
            "Simon S. Woo",
            "Jong Hwan Ko"
        ],
        "venue_full": "International Joint Conference on Neural Networks",
        "venue": "IJCNN",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/ijcnn60899.2024.10649922"
        },
        "img": "/img/Publications/ijcnn.png",
        "abstract": "Online video detection becomes more challenging with higher resolution as computational costs increase proportionally with increasing resolution. To address this issue, we present a novel approach, DynaPP, which arranges object candidate regions into a compact form. DynaPP performs resource intensive whole-image inference only on sparse key frames, employing reduced resolutions for inference on other frames. Additionally, we propose transforming a 1-stage detector into a dynamic resolution model to facilitate frame inference at reduced resolutions. Here, the dynamic resolution model signifies a model capable of inferring all resolutions, distinguishing itself from typical models by not having restricted inferable resolutions. Unlike prior studies introducing new model structures for multi-resolution models, our work demonstrates that slight modifications to existing models can convert them to dynamic resolution models. DynaPP showcases substantial acceleration in video detection across four representative video datasets: AUAIR (5.5×), UAVDT (3.67×), VisDrone (2.73×), and ImageNet VID (3.69×), while maintaining a mean average precision with a small loss (≤2.2). Furthermore, we observed that our method achieves a detection acceleration of up to 8.84×, depending on the video clip."
    },
    {
        "title": "Disrupting Diffusion-based Inpainters with Semantic Digression",
        "authors": [
            "Geonho Son",
            "Juhun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "International Joint Conference on Artificial Intelligence",
        "venue": "IJCAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2407.10277"
        },
        "img": "/img/Publications/ijcai24_joseph.jpg",
        "abstract": "The fabrication of visual misinformation on the web and social media has increased exponentially with the advent of foundational text-to-image diffusion models. Namely, Stable Diffusion inpainters allow the synthesis of maliciously inpainted images of personal and private figures, and copyrighted contents, also known as deepfakes. To combat such generations, a disruption framework, namely Photoguard, has been proposed, where it adds adversarial noise to the context image to disrupt their inpainting synthesis. While their framework suggested a diffusion-friendly approach, the disruption is not sufficiently strong and it requires a significant amount of GPU and time to immunize the context image. In our work, we re-examine both the minimal and favorable conditions for a successful inpainting disruption, proposing DDD, a \"Digression guided Diffusion Disruption\" framework. First, we identify the most adversarially vulnerable diffusion timestep range with respect to the hidden space. Within this scope of noised manifold, we pose the problem as a semantic digression optimization. We maximize the distance between the inpainting instance's hidden states and a semantic-aware hidden state centroid, calibrated both by Monte Carlo sampling of hidden states and a discretely projected optimization in the token space. Effectively, our approach achieves stronger disruption and a higher success rate than Photoguard while lowering the GPU memory requirement, and speeding the optimization up to three times faster."
    },
    {
        "title": "iFakeDetector: Real Time Integrated Web-based Deepfake Detection System",
        "authors": [
            "Kangjun Lee",
            "Inho Jung",
            "Simon S. Woo"
        ],
        "venue_full": "International Joint Conference on Artificial Intelligence",
        "venue": "IJCAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.24963/ijcai.2024/1016"
        },
        "img": "/img/Publications/kangjun_ijcai24.png",
        "abstract": "Deepfake detection research has been actively conducted in the past. While many deepfake detectors have been proposed, validating the practicality of such systems against real-world settings has not been explored much. Indeed, there might be gaps and disparities when they are applied in the real world. In this work, we developed a real time integrated web-based deepfake detection system, iFakeDetector, which incorporates the recent high performing deepfake detectors, and enables easy access for non-expert users to evaluate deepfake videos. Our system takes a deepfake video as input, allowing users to upload videos and select different detectors, and provides detection results on whether the uploaded video is a deepfake or not. Furthermore, we provide an analysis tool that enables the video to be analyzed on a frame-by-frame basis with the probability of each frame being manipulated. Finally, we tested and deployed iFakeDetector in a real-world scenario to verify its practicality and feasibility."
    },
    {
        "title": "Gradient Alignment for Cross-Domain Face Anti-Spoofing",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF Conference on Computer Vision and Pattern Recognition",
        "venue": "CVPR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/cvpr52733.2024.00026"
        },
        "img": "/img/Publications/binh_cvpr24.png",
        "abstract": "Recent advancements in domain generalization (DG) for face anti-spoofing (FAS) have garnered considerable attention. Traditional methods have focused on designing learning objectives and additional modules to isolate domain-specific features while retaining domain-invariant characteristics in their representations. In this paper, we introduce GAC-FAS, a novel learning objective that encourages the model to converge towards an optimal flat minimum without necessitating additional learning modules. Unlike conventional sharpness-aware minimizers, GAC-FAS identifies ascending points for each domain and regulates the generalization gradient updates at these points to align coherently with empirical risk minimization (ERM) gradient updates. This unique approach specifically guides the model to be robust against domain shifts. We demonstrate the efficacy of GAC-FAS through rigorous testing on challenging cross-domain FAS datasets, where it establishes state-of-the-art performance."
    },
    {
        "title": "Beyond the Screen: Evaluating Deepfake Detectors under Moiré Pattern Effects",
        "authors": [
            "Razaib Tariq",
            "Minji Heo",
            "Simon S. Woo",
            "Shahroz Tariq"
        ],
        "venue_full": "CVPR Workshop on Media Forensics",
        "venue": "CVPRW",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/cvprw63382.2024.00446"
        },
        "img": "/img/Publications/Moire_CVPR_Workshop.png",
        "abstract": "The detection of deepfakes is crucial for mitigating the societal impact of falsified video content. Despite the development of various algorithms for this purpose, challenges arise for detectors in real-world scenarios, especially when users capture deepfake content from screens and upload it online or when detectors operate on external devices like smartphones, requiring the capture of potential deepfakes through the camera for evaluation. A significant challenge in these scenarios is the presence of Moir ́e patterns, which degrade image quality and complicate conventional classification methods, notably deep neural networks (DNNs). However, the impact of Moir ́e patterns on the effectiveness of deepfake detection systems has not been adequately explored. This study aims to investigate how capturing deepfake videos via digital screen cameras affects the accuracy of detection mechanisms. We introduced the Moir ́e patterns by capturing the display of a monitor using a smartphone camera and conducted empirical evaluations using four widely recognized datasets: CelebDF, DFD, DFDC, and FF++. We compare the performance of twelve SOTA detectors on deepfake videos captured under the influence of Moir ́e patterns. Our findings reveal a performance decrease of up to 33.1 and 31.3 percentage points for image and video-based detectors. Therefore, highlighting the challenges posed by Moir ́e patterns and other naturally induced artifacts is critical for improving the effectiveness of real-world deepfake detection effort."
    },
    {
        "title": "Revisiting 30 years of the Network Time Protocol",
        "authors": [
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3589335.3651998"
        },
        "img": "/img/Publications/simon_theweb24.png",
        "abstract": "Since the inception of the Internet and WWW, providing the time among multiple nodes on the Internet has been one of the most critical challenges. David Mills is the pioneer to provide time on the Internet, inventing the Network Time Protocol (NTP), and synchronizing the clocks in computer systems. Now, the NTP is predominantly used on the Internet and WWW. In this paper, we revisit the NTP, and present the overview of the NTP. And, we highlight the advanced research effort, the SpaceNTP, to synchronize the clocks among space assets, which is the fundamental medium to provide the web services in space."
    },
    {
        "title": "Saliency-Aware Time Series Anomaly Detection for Space Applications",
        "authors": [
            "Sangyup Lee",
            "Simon S. Woo"
        ],
        "venue_full": "Pacific-Asia Conference on Knowledge Discovery and Data Mining",
        "venue": "PAKDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-97-2242-6_26"
        },
        "img": "/img/Publications/sam_pakdd2024.png",
        "abstract": "Our proposed method utilizes saliency detection,\nsimilar to anomaly detection, to identify the most significant region and effectively detect abnormal data. In this work, We propose a novel\nframework, Saliency-aware Anomaly Detection (SalAD), for detecting anomalies in multivariate time series data. SalAD comprises three main\ncomponents: 1) a saliency detection module to remove redundant data, 2) an unsupervised saliency-aware forecasting model, and 3) a saliencyaware\nanomaly score to differentiate anomalies. We evaluate our model using the real-world Korea Aerospace Research Institute (KARI) orbital element dataset, which includes six orbital elements and unexpected disturbances from satellites, as well as conducting extensive experiments on four benchmark datasets to demonstrate its effectiveness and superiority over other baselines. The SalAD framework has been deployed on the K3A and K5 satellites."
    },
    {
        "title": "SEE: Spherical Embedding Expansion for Improving Deep Metric Learning",
        "authors": [
            "Binh Minh Le",
            "Simon S. Woo"
        ],
        "venue_full": "Pacific-Asia Conference on Knowledge Discovery and Data Mining",
        "venue": "PAKDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-97-2253-2_11"
        },
        "img": "/img/Publications/binhle_pakdd2024.png",
        "abstract": "The primary goal of deep metric learning is to construct a comprehensive embedding space that can effectively represent samples originating from both intra- and inter-classes. Although extensive prior work has explored diverse metric functions and innovative training strategies, much of this work relies on default training data. Consequently, the potential variations inherent within this data remain largely unexplored, constraining the model's robustness to unseen images.In this context, we introduce the Spherical Embedding Expansion (dubbed SEE) method. SEE aims to uncover the latent semantic variations in training data. Especially, our method augments the embedding space with synthetic representations based on Max-Mahalanobis distribution (MMD) centers, which maximize the dispersion of these synthetic features without increasing computational costs."
    },
    {
        "title": "Relation-Aware Label Smoothing for Self-KD",
        "authors": [
            "Jeongho Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Pacific-Asia Conference on Knowledge Discovery and Data Mining",
        "venue": "PAKDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-97-2253-2_16"
        },
        "img": "/img/Publications/jeongho_kdd2024.jpg",
        "abstract": "Although self-knowledge distillation shows remarkable performance improvement with fewer resources than conventional teacher-student based KD approaches, existing self-KD methods still require additional time and memory for training. We propose Relation-Aware Label Smoothing for Self-Knowledge Distillation (RAS-KD) that regularizes the student model itself by utilizing the inter-class relationships between class representative vectors with a light-weight auxiliary classifier. Compared to existing self-KD methods that only consider the instance-level knowledge, we show that proposed global-level knowledge is sufficient to achieve competitive performance while being extremely efficient training cost. Also, we achieve extra performance improvement through instance-level supervision."
    },
    {
        "title": "STLGRU: Spatio-Temporal Lightweight Graph GRU for Traffic Flow Prediction",
        "authors": [
            "Kishor Kumar Bhaumik",
            "Fahim Faisal Niloy",
            "Saif Mahmud",
            "Simon S. Woo"
        ],
        "venue_full": "Pacific-Asia Conference on Knowledge Discovery and Data Mining",
        "venue": "PAKDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-97-2266-2_23"
        },
        "img": "/img/Publications/kishor_pakdd2024.png",
        "abstract": "We propose Spatio-Temporal Lightweight Graph GRU, namely STLGRU,\na novel traffic forecasting model for predicting traffic flow accurately. Specifically, our proposed STLGRU can effectively capture dynamic local and global spatial-temporal relations of traffic networks using memory-augmented attention and gating mechanism in a continuously synchronized manner. Moreover, instead of employing separate temporal and spatial components, we show that our memory module and gated unit can successfully learn the spatial-temporal dependencies, with reduced memory usage and fewer parameters. Extensive experimental results on three real-world public traffic datasets demonstrate that our method can not only achieve state-of-the-art performance but also exhibit competitive computational efficiency."
    },
    {
        "title": "Development of Deep Learning-based Algorithm for Extracting Abnormal Deceleration Patterns",
        "authors": [
            "Youngho Jun",
            "Minha Kim",
            "Kangjun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "International Electric Vehicle Symposium & Exhibition",
        "venue": "EVS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1007/978-981-97-2266-2_23"
        },
        "img": "/img/Publications/minha_EVS37.png",
        "abstract": "The smart regenerative braking system for EV can reduce unnecessary brake operation by assisting in braking of the vehicle according to the driving situation, road slope, and driver’s preference. This system maintains the distance between the ego and front vehicles without controlling the brake pedal. Since the strength of regenerative braking is generally determined based on calibration data determined during the vehicle development process, some driver could suffer inconvenience when the regenerative braking is activated differently from their driving habits. In order to solve this problem, various deep learning-based algorithms are developed to provide driving stability by learning the driving data. Among those artificial intelligence algorithms, anomaly detection algorithms can successfully separate the deceleration data in abnormal driving situations, and the resulting refined deceleration data can be used to train the regression model to achieve better driving stability. In this study, we extensively compare and evaluate the performance of clustering and anomaly detection methods."
    },
    {
        "title": "Source-Free Online Domain Adaptive Semantic Segmentation of Satellite Images Under Image Degradation",
        "authors": [
            "Fahim Faisal Niloy",
            "Kishor Kumar Bhaumik",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE International Conference on Acoustics, Speech and Signal Processing",
        "venue": "ICASSP",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/icassp48485.2024.10447965"
        },
        "img": "/img/Publications/kishor_icassp24.jpg",
        "abstract": "In this paper, we address source-free and online domain adaptation, i.e., test-time adaptation (TTA), for satellite im- ages subject to various forms of image degradation. Towards achieving this goal, we propose a novel TTA approach involv- ing two effective strategies. First, we progressively estimate the global Batch Normalization (BN) statistics of the target distribution with incoming data stream. Leveraging these statistics during inference has the ability to effectively reduce domain gap. Furthermore, we enhance prediction quality by refining the predicted masks using global class centers. Both strategies employ dynamic momentum for fast and stable convergence. Notably, our method is back-propagation-free and hence fast and lightweight, making it highly suitable for on-the-fly adaptation to new domain. Through comprehen- sive experiments across various domain adaptation scenarios, we demonstrate the robust performance of our method."
    },
    {
        "title": "All but One: Surgical Concept Erasing with Model Preservation in Text-to-Image Diffusion Models",
        "authors": [
            "SeungHoo Hong",
            "Juhun Lee",
            "Simon S. Woo"
        ],
        "venue_full": "AAAI Conference on Artificial Intelligence",
        "venue": "AAAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1609/aaai.v38i19.30107"
        },
        "img": "/img/Publications/joseph_aaai23.jpg",
        "abstract": "Text-to-Image models such as Stable Diffusion have shown impressive image generation synthesis, thanks to the utilization of large-scale datasets. However, these datasets may contain sexually explicit, copyrighted, or undesirable content, which allows the model to directly generate them. Given that retraining these large models on individual concept deletion requests is infeasible, fine-tuning algorithms have been developed to tackle concept erasing in diffusion models. While these algorithms yield good concept erasure, they all present one of the following issues: 1) the semantics of the prompts change over time, 2) long and inefficient training exposes the model to more harm, and 3) the spatial structure distribution of each generated image is not preserved after fine-tuning. These issues severely degrade the original utility of generative models. In this work, we present a new approach that solves all of these challenges. We take inspiration from the concept of classifier guidance and propose a surgical update on the classifier guidance term while constraining the unconditional score term. Furthermore, our algorithm empowers the user to select an alternative to the erasing concept, allowing for more controllability. Our experimental results show that our algorithm not only erases the target concept effectively but also preserves the model's generation capability."
    },
    {
        "title": "Layer Attack Unlearning: Fast and Accurate Machine Unlearning via Layer Level Attack and Knowledge Distillation",
        "authors": [
            "Hyunjune Kim",
            "Sangyong Lee",
            "Simon S. Woo"
        ],
        "venue_full": "AAAI Conference on Artificial Intelligence",
        "venue": "AAAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1609/aaai.v38i19.30118"
        },
        "img": "/img/Publications/kim_aaai23.jpg",
        "abstract": "In this work, we propose a fast and novel machine unlearning paradigm at the layer level called layer attack unlearning, which is highly accurate and fast compared to existing machine unlearning algorithms. We introduce the Partial-PGD algorithm to locate the samples to forget efficiently. In addition, we only use the last layer of the model inspired by the Forward-Forward algorithm for unlearning process. Lastly, we use Knowledge Distillation (KD) to reliably learn the decision boundaries from the teacher using soft label information to improve accuracy performance. We conducted extensive experiments with SOTA machine unlearning models and demonstrated the effectiveness of our approach for accuracy and end-to-end unlearning performance."
    },
    {
        "title": "Blind-Touch: Homomorphic Encryption-Based Distributed Neural Network Inference for Privacy-Preserving Fingerprint Authentication",
        "authors": [
            "Hyunmin Choi",
            "Simon S. Woo",
            "Hyoungshick Kim"
        ],
        "venue_full": "AAAI Conference on Artificial Intelligence",
        "venue": "AAAI",
        "track": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1609/aaai.v38i20.30200"
        },
        "img": "/img/Publications/choi_aaai23.jpg",
        "abstract": "This paper introduces Blind-Touch, a novel machine learning-based fingerprint authentication system that leverages homomorphic encryption to address these privacy concerns. Homomorphic encryption allows for computations on encrypted data without decrypting it. Therefore, Blind-Touch can keep fingerprint data encrypted on the server while performing machine learning operations. Blind-Touch integrates three techniques to address the computational challenges of using homomorphic encryption for machine learning: (1) A distributed machine learning architecture that divides inference tasks between the client and server, thereby reducing encrypted computations on the server; (2) A data compression method that reduces client-server communication costs; and (3) A cluster architecture that improves scalability with the number of registered users. Blind-Touch achieves high accuracy on two benchmark fingerprint datasets, with a 93.6% F1-score for the PolyU dataset and a 98.2% F1-score for the SOKOTO dataset. Moreover, Blind-Touch can match a fingerprint among 5,000 in about 0.65 seconds.With its privacyfocused design, high accuracy, and efficiency, Blind-Touch is a promising alternative to conventional fingerprint authentication\nfor web and cloud applications."
    },
    {
        "title": "Hardening Interpretable Deep Learning Systems: Investigating Adversarial Threats and Defenses",
        "authors": [
            "Eldor Abdukhamidov",
            "Mohammed Abuhamad",
            "Simon S. Woo",
            "Eric Chan-Tin",
            "Tamer Abuhmed"
        ],
        "venue_full": "IEEE Transactions on Dependable and Secure Computing",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            6.8
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/tdsc.2023.3341090"
        },
        "img": "/img/Publications/Hardening Interpretable.png",
        "abstract": "This work introduces two attacks, AdvEdge and AdvEdge+, which deceive both the target deep learning model and the coupled interpretation model. We assess the effectiveness of proposed attacks against four deep learning model architectures coupled with four interpretation models that represent different categories of interpretation models. Our experiments include the implementation of attacks using various attack frameworks. We also explore the attack resilience against three general defense mechanisms and potential countermeasures. Our analysis shows the effectiveness of our attacks in terms of deceiving the deep learning models and their interpreters, and highlights insights to improve and circumvent the attacks."
    },
    {
        "title": "RAAD: Reinforced Adversarial Anomaly Detector",
        "authors": [
            "Simon S Woo",
            "Daeyoung Yoon",
            "Yuseung Gim",
            "Eunseok Park"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3605098.3635920"
        },
        "img": "/img/Publications/RAAD.png",
        "abstract": "We propose a novel framework called Reinforced Adversarial Anomaly Detector (RAAD) based on Reinforcement Learning to mine and detect anomalies or attacks in the presence of very few attack or anomaly patterns in time-series. Our approach uses two adversarial agents, where one agent acts as an attacker and the other as a defender. The attacker agent learns a policy to disturb the defender agent by effectively sampling the defender’s worst-performing trajectories from synthetically generated states provided by the environment, while the defender agent learns a policy that can distinguish between the normal and abnormal (attack) states. Upon successful training of two adversarial policies, the defender agent can effectively evaluate whether a new observation follows the distribution of normal states. In particular, RAAD overcomes the inherent overfitting issue, which other approaches have, through adversarial training and Reinforcement Learning. Using multiple real-world anomaly and attack detection datasets, we demonstrate that RAAD outperforms the several other baseline approaches in identifying abnormal patterns."
    },
    {
        "title": "Action Attention GRU: A Data-Driven Approach for Enhancing Purchase Predictions in Digital Marketing",
        "authors": [
            "Girim Ban",
            "Simon S Woo",
            "David Sung"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1145/3605098.3635958"
        },
        "img": "/img/Publications/AAGRU.png",
        "abstract": "We present a data-driven model, the Action Attention bidirectional Gated Recurrent Unit (AAGRU) to effectively learn sequences of user behaviors without explicit knowledge of the actors or targets for conversion prediction. Tailored to predict impending purchases based on ADID’s customer journey, AAGRU leverages two pivotal components: the Action Block and the Interval Block. The former adeptly captures salient actions in the journey through attention mechanisms, while the latter discerns temporal nuances, such as impulse and deliberate buying tendencies. This tailored approach enables digital marketing agencies to identify latent customers primed for purchase, thus optimizing targeted advertising and conversion strategies. Our experimental results affirm AAGRU’s superiority over extant deep learning models. Significantly, in simulations, AAGRU demonstrated impressive performance against our company’s best audience group."
    },
    {
        "title": "Real-Time User-guided Adaptive Colorization with Vision Transformer",
        "authors": [
            "Gwanghan Lee",
            "Saebyeol Shin",
            "Taeyoung Na",
            "Simon S. Woo"
        ],
        "venue_full": "2024 IEEE/CVF Winter Conference on Applications of Computer Vision",
        "venue": "WACV",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/wacv57701.2024.00054"
        },
        "img": "/img/Publications/Screen Shot 2023-11-25 at 2.52.37 PM.png",
        "abstract": "We propose a novel efficient ViT architecture for real-time interactive colorization, AdaColViT determines which redundant image patches and layers to reduce in the ViT. Unlike existing methods, our novel pruning method alleviates performance drop and flexibly allocates computational resources of input samples, effectively achieving actual acceleration. In addition, we demonstrate through extensive experiments on ImageNet-ctest10k, Oxford 102flowers, and CUB-200 datasets that our method outperforms the baseline methods."
    },
    {
        "title": "EAE-GAN: Emotion-Aware Emoji Generative Adversarial Network for Computational Modeling Diverse and Fine-Grained Human Emotions",
        "authors": [
            "SangEun Lee",
            "Seoyun Kim",
            "Yeonju Chu",
            "JeongWon Choi",
            "Eunil Park",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Transactions on Computational Social Systems",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            5.0
        ],
        "year": 2024,
        "links": {
            "conf": "https://doi.org/10.1109/tcss.2023.3329434"
        },
        "img": "/img/Publications/TCS.png",
        "abstract": "With the growing ubiquity and broad usage, emojis are widely used as a universal visual language, which complements the intentions and emotions beyond the textual data. Despite the critical role of representing emotion, existing emojis neglect the subtle and complex properties of human emotion in that only countable and finite face emojis exist in a categorical manner. In this article, we propose a novel approach to facial emoji generation, which can control the emotional degree of generated emojis for more complex and detailed usage on online conversations. In other words, we develop a new emotion aware emoji generative adversarial network, which is capable of generating an emoji that expresses a given emotion distribution. In this way, our approach aims to map fine grained emotions to expressive emojis. Both quantitative and qualitative evaluation demonstrate that our approach can successfully generate high quality emoji like images by representing a wide range of emo tions. To the best of our knowledge, this is the first approach to use the deep generative model from the standpoint of the emoji’s emotional role, which can further promote more interactive and effective online communication."
    },
    {
        "title": "Extreme Environment Rotated Object Detection Network",
        "authors": [
            "Giljun Lee",
            "Junyaup Kim",
            "Gwanghan Lee",
            "Simon S. Woo"
        ],
        "venue_full": "Journal of KIISE",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.5626/jok.2023.50.11.966"
        },
        "img": "/img/Publications/E^2RDet.png",
        "abstract": "This paper proposes E^2RDet. This algorithm effectively modifies the structure of the Yolov7 object detection model, enabling it to accurately detect objects represented by oriented bounding boxes (OBB) in SAR images. This algorithm improves the object detection model architecture and loss function to facilitate learning of an object's dynamic (orientation) posture. Using various training datasets, E^2RDet demonstrates performance improvements across three benchmark SAR datasets. This indicates that existing HBB object detection models can train and perform object detection on objects represented by OBBs."
    },
    {
        "title": "KappaFace: Adaptive Additive Angular Margin Loss for Deep Face Recognition",
        "authors": [
            "Chingis Oinar",
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.47
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/access.2023.3338648"
        },
        "img": "/img/Publications/ching_TIP23.png",
        "abstract": "Imbalanced learning might include both classes having different learning difficulties or different numbers of available training samples. We hypothesize that it significantly affects the generalization ability of the deep face models. Inspired by this, we introduce a novel adaptive strategy, called KappaFace, to modulate the relative importance based on class learning difficulty and its imbalance. Due to the von Mises-Fisher distribution, our proposed KappaFace loss can intensify margins for difficult-to-learn or under-represent classes while relaxing that of counter classes. Experiments conducted on popular facial benchmarks demonstrate that our proposed method achieves superior performance to the state-of-the-art methods."
    },
    {
        "title": "Occupational Gender Bias in Large Language Models evaluated on multiple languages",
        "authors": [
            "Seung-yeon Back",
            "Eun-Ju Park",
            "Simon S. Woo"
        ],
        "venue_full": "ACM CIKM Workshop on Large Language Models’ Interpretation and Trustworthiness",
        "venue": "LLIMT",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {},
        "img": "/img/Publications/seungyeon_llm.png",
        "abstract": "In our study, we turn our attention specifically to the bias issues at the intersection of gender and occupations within LLM-generated text. Our research seeks to address this concern by examining how gender bias is reflected in responses generated by LLMs, with a focus on the fields of gender and occupation. We aim to explore these biases not only in English, but also in Korean language, thereby expanding the scope of our investigation to different linguistic and cultural contexts. Through these investigations, our research aims to provide a comprehensive comparison of bias patterns across different languages and cultures. Ultimately, we seek to contribute to the ongoing dialogue surrounding ethical concerns in LLMs and offer implications for future developments in the field of natural language processing."
    },
    {
        "title": "Anomaly and Novelty detection for Satellite and Drone systems (ANSD '23)",
        "authors": [
            "Shahroz Tariq",
            "Daewon Chung",
            "Simon S. Woo",
            "Youjin Shin"
        ],
        "venue_full": "ACM Workshop on International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3583780.3615306"
        },
        "img": "/img/Publications/Call For Papers.png",
        "abstract": "In recent times, there has been a notable surge in the amount of vision and sensing/time-series data obtained from drones and satellites. This data can be utilized in various fields, such as precision agriculture, disaster management, environmental monitoring, and others. However, the analysis of such data poses significant challenges due to its complexity, heterogeneity, and scale. Furthermore, it is critical to identify anomalies and maintain/monitor the health of drones and satellite systems to enable the aforementioned applications and sciences. This workshop presents an excellent opportunity to explore solutions that specifically target the detection of anomalies and novel occurrences in drones and satellite systems and their data. The workshop is designed to promote knowledge exchange, collaboration, and innovation in Anomaly and Novelty detection for Satellite and Drone systems. Through this platform, researchers, practitioners, and industry experts are expected to come together to explore and discuss the latest developments, challenges, and opportunities in analyzing and maintaining the health of drone and satellite systems, in addition to detecting anomalies and novelties in the associated vision and time-series data. The primary objective of the workshop is to facilitate in-depth discussions on various techniques, methodologies, and applications related to anomaly and novelty detection. Participants will be encouraged to share their ideas and experiences on how best to identify new research directions and potential collaborations. Ultimately, the workshop aims to enhance the capabilities of leveraging drone and satellite systems for diverse applications such as precision agriculture, disaster management, and environmental monitoring. By the end of the workshop, participants are expected to gain valuable insights into state-of-the-art approaches and establish connections with peers. This will provide an opportunity for them to contribute to the advancement of knowledge in this domain, leading to more efficient and effective utilization of drone and satellite systems. For more information, visit our website at ANSD'23."
    },
    {
        "title": "KID34K: A Dataset for Online Identity Card Fraud Detection",
        "authors": [
            "Eun-Ju Park",
            "Seung-Yeon Back",
            "Jeongho Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3583780.3615122"
        },
        "img": "/img/Publications/kid34k_cikm23.jpg",
        "abstract": "To mitigate the risks associated with fraudulent ID card verification, we present a novel dataset for classifying cases where the ID card images that users upload to the verification system are genuine or digitally represented. Our dataset is replicas designed to resemble real ID cards, making it available while avoiding privacy issues. Through extensive experiments, we demonstrate that our dataset is effective for detecting digitally represented ID card images, not only in our replica dataset but also in the dataset consisting of real ID cards."
    },
    {
        "title": "UNDO: Effective and Accurate Unlearning Method for Deep Neural Networks",
        "authors": [
            "Sangyong Lee",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3583780.3615235"
        },
        "img": "/img/Publications/undo_cikm23.jpg",
        "abstract": "In this work, we propose a novel two-step unlearning approach UNDO. First, we selectively disrupt the decision boundary of forgetting data at the coarse-grained level. However, this can also inadvertently affect the decision boundary of other remaining data, lowering the overall performance of classification task. Hence, we subsequently repair and refining the decision boundary for each class at the fine-grained level by introducing a loss for maintain the overall performance, while completely removing the class. We conducted extensive experiments with SOTA models over two datasets, and demonstrated the effectiveness and efficiency of our approach for unlearning, compared to other methods."
    },
    {
        "title": "SAFE: Sequential Attentive Face Embedding with Contrastive Learning for Deepfake Video Detection",
        "authors": [
            "Juho Jung",
            "Chaewon Kang",
            "Jeewoo Yoon",
            "Simon S. Woo",
            "Jinyoung Han"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Short Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3583780.3615279"
        },
        "img": "/img/Publications/safe_cikm23.png",
        "abstract": "This paper proposes a novel sequential attentive face\nembedding, SAFE, that can capture facial dynamics in a deepfake video. The proposed SAFE can effectively integrate global and local dynamics of facial features revealed in a video sequence using contrastive learning. Through a comprehensive comparison with the state-of-the-art methods on the DFDC (Deepfake Detection\nChallenge) dataset and the FaceForensic++ benchmark, we show that our model achieves the highest accuracy in detecting deepfake videos on both datasets."
    },
    {
        "title": "Towards Understanding of Deepfake Videos in the Wild",
        "authors": [
            "Beomsang Cho",
            "Binh M. Le",
            "Jiwon Kim",
            "Simon S. Woo",
            "Shahroz Tariq",
            "Alsharif Abuadbba",
            "Kristen Moore"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2309.01919"
        },
        "img": "/img/Publications/rwdf23_cikm23.png",
        "abstract": "Our contributions in this IRB-approved study are to bridge this knowledge gap from current real-world deepfakes by providing in-depth analysis.We first present the largest and most diverse and recent deepfake dataset (RWDF-23) collected from the wild to date, consisting of 2,000 deepfake videos collected from 4 platforms targeting 4 different languages span created from 21 countries: Reddit, YouTube, TikTok, and Bilibili. By expanding the dataset's scope beyond the previous research, we capture a broader range of real-world deepfake content, reflecting the ever-evolving landscape of online platforms. Also, we conduct a comprehensive analysis encompassing various aspects of deepfakes, including creators, manipulation strategies, purposes, and real-world content production methods. This allows us to gain valuable insights into the nuances and characteristics of deepfakes in different contexts. Lastly, in addition to the video content, we also collect viewer comments and interactions, enabling us to explore the engagements of internet users with deepfake content."
    },
    {
        "title": "Quality-Agnostic Deepfake Detection with Intra-model Collaborative Learning",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF International Conference on Computer Vision",
        "venue": "ICCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/iccv51070.2023.02045"
        },
        "img": "/img/Publications/qad_iccv23_arch.png",
        "abstract": "In this work, we propose a universal intra-model collaborative learning framework to enable the effective and simultaneous detection of different quality of deepfakes. That is, our approach is the quality-agnostic deepfake detection method, dubbed QAD. In particular, by observing the upper bound of general error expectation, we maximize the dependency between intermediate representations of images from different quality levels via Hilbert-Schmidt Independence Criterion. In addition, an Adversarial Weight Perturbation module is carefully devised to enable the model to be more robust against image corruption while boosting the overall model’s performance. Extensive experiments over seven popular deepfake datasets demonstrate the superiority of our QAD model over prior SOTA benchmarks."
    },
    {
        "title": "Manipulated ID Card Classification using Deep Neural Networks",
        "authors": [
            "Hakjun Moon",
            "Eunju Park",
            "Jeongho Kim",
            "Kwansik Yoon",
            "Yeonah Seo",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Summer",
        "venue": "CISC-S",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {},
        "img": "/img/Publications/moon_hanconf23.png",
        "abstract": "2023 한국정보보호학화 하계학술대회 딥러닝 기반 신원 인증 시스템에 대해 제시하였으며, 비대면 상황에서 주민등록증이나 운전면허증과 같은 신분증의 진위를 확인하는 문제에 집중하였다. 딥러닝과 특징 추출 기법을 이용하여 신분증 이미지가 실물인지, 혹은 디지털 방식으로 조작되었는지 판별하도록 모델을 학습하였으며, 최대 96.6%의 높은 분류 정확도를 보였다. 이런 결과는 신원 인증과 보안의 중요성이 갈수록 부각되는 현재 사회에서 중요한 의미를 가진다."
    },
    {
        "title": "Selective unlearning for DNN based model",
        "authors": [
            "Song-Chan Jin",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Summer",
        "venue": "CISC-S",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {},
        "img": "/img/Publications/songchan_hanconf23.png",
        "abstract": "본 논문에서 제안하는 선택적 망각이란 딥러닝 모델이 일부 지식을 선택적으로 잊어버리는 것을 의미하며, 개인정보 보호를 위해 도입되었다. 이를 위해 데이터 재수정 및 모델 재학습 등의 방법이 있지만, 이러한 방법들은 일반적으로 계산량이 많거나 모델의 성능을 크게 저하시키는 문제가 있어서 이에 대한 대안으로 작은 데이터셋으로 다른 데이터들에 대한 지식은 유지한 채 특정 데이터들에 대한 지식만 잊는 경사 상승법을 소개하고 있다. 본 논문에서는 경사 상승법을 통하여 기존 재학습 기법 대비 9배 적은 계산량으로 선택적 망각을 수행할 수 있다는 결과를 얻었다."
    },
    {
        "title": "HRFNet: High-Resolution Forgery Network for Localizing Satellite Image Manipulation",
        "authors": [
            "Fahim Faisal Niloy",
            "Kishor Kumar Bhaumik",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE International Conference on Image Processing",
        "venue": "ICIP",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/icip49359.2023.10221974"
        },
        "img": "/img/Publications/hrfnet_arch.png",
        "abstract": "Existing high-resolution satellite image forgery localization methods rely on patch-based or downsampling-based training. Both of the training methods have major drawbacks, such as, inaccurate boundary between pristine and forged region, generation of unwanted artifacts, etc. To tackle aforementioned challenges, inspired from the high-resolution image segmentation literature, we propose a novel model called HRFNet to effectively enable satellite image forgery localization. Specifically, equipped with shallow and deep branches, our model can successfully integrate RGB and resampling features in both global and local manner to localize forgery more accurately. We experiment on popular satellite image manipulation dataset to demonstrate that our method achieves the best performance, while the memory requirement and processing speed are not compromised compared to existing methods."
    },
    {
        "title": "Expectation-Maximization via Pretext-Invariant Representations",
        "authors": [
            "Chingis Oinar",
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.47
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/access.2023.3289589"
        },
        "img": "/img/Publications/empir_arch.png",
        "abstract": "In this work, we explain and propose a novel self-supervised objective, Expectation-Maximization via Pretext-Invariant Representations (Empir), which enhances Expectation-Maximization-based optimization in BYOL-like algorithms by enforcing augmentation invariance within a local region of k nearest neighbors, resulting in consistent representation learning. In other words, we propose Expectation-Maximization as a core task of asymmetric architectures. We show that it consistently outperforms other SOTA algorithms by a decent margin. We also demonstrate its transfer learning capabilities on downstream image recognition tasks."
    },
    {
        "title": "IMF: Integrating Matched Features Using Attentive Logit in Knowledge Distillation",
        "authors": [
            "Jeongho Kim",
            "Hanbeen Lee",
            "Simon S. Woo"
        ],
        "venue_full": "International Joint Conference on Artificial Intelligence",
        "venue": "IJCAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.24963/ijcai.2023/108"
        },
        "img": "/img/Publications/imf_ijcai.png",
        "abstract": "In this work, to address the student model's limitation, we propose a novel flexible KD framework, Integrating Matched Features using Attentive Logit in Knowledge Distillation (IMF). Our approach introduces an intermediate feature distiller (IFD) to improve the overall performance of the student model by directly distilling the teacher's knowledge into branches of student models.The generated output of IFD, which is trained by the teacher model, is effectively combined by attentive logit.We use only a few blocks of the student and the trained IFD during inference, requiring an equal or less number of parameters.Through extensive experiments, we demonstrate that IMF consistently outperforms other state-of-the-art methods with a large margin over the various datasets in different tasks without extra computation."
    },
    {
        "title": "Exploiting Inconsistencies in Object Representations for Deepfake Video Detection",
        "authors": [
            "Kishor Kumar Bhaumik",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3595353.3595885"
        },
        "img": "/img/Publications/wdc_kishor.png",
        "abstract": "Deepfake videos are mostly generated in a frame-by-frame manner, which leaves visible object-level inconsistencies in both temporal and spatial dimensions. In this paper, we propose a novel deepfake video detection method that exploits this important clue. Specifically, we extract object representations using vision transformers from video frames and then model the object-level coherence in both intra-frame and inter-frame manner. We experiment on benchmark dataset to show that our method outperforms several existing methods in deepfake video detection."
    },
    {
        "title": "Why Do Facial Deepfake Detectors Fail?",
        "authors": [
            "Binh Le",
            "Shahroz Tariq",
            "Alsharif Abuadbba",
            "Kristen Moore",
            "Simon Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3595353.3595882"
        },
        "img": "/img/Publications/face_detect_engine.png",
        "abstract": "Recent rapid advancements in deepfake technology have allowed the creation of highly realistic fake media, such as video, image, and audio. These materials pose significant challenges to human authentication, such as impersonation, misinformation, or even a threat to national security. To keep pace with these rapid advancements, several deepfake detection algorithms have been proposed, leading to an ongoing arms race between deepfake creators and deepfake detectors. Nevertheless, these detectors are often unreliable and frequently fail to detect deepfakes. This study highlights the challenges they face in detecting deepfakes, including (1) the pre-processing pipeline of artifacts and (2) the fact that generators of new, unseen deepfake samples have not been considered when building the defense models. Our work sheds light on the need for further research and development in this field to create more robust and reliable detectors."
    },
    {
        "title": "Distance adaptive graph convolutional gated network-based smart air quality monitoring and health risk prediction in sensor-devoid urban areas",
        "authors": [
            "Shahzeb Tariq",
            "Shahroz Tariq",
            "SangYoun Kim",
            "Simon S. Woo",
            "ChangKyoo Yoo"
        ],
        "venue_full": "Journal of Sustainable Cities and Society",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            10.696
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1016/j.scs.2023.104445"
        },
        "img": "/img/Publications/tariq_civil.png",
        "abstract": "Rapid urbanization and economic growth have increased air pollution, threatening human health and life expectancy, especially in developing nations. Strong air quality early warning systems for city sustainability have recently garnered attention. The present early warning frameworks in urban environments can only forecast air quality where sufficient sensor data is available. We propose a spatiotemporal sensor fusion-based distance adaptive graph convolutional gated network that predicts primary pollutants at multiple megacity locations and temporal horizons. Our remotely forecasted concentrations at a sensorless site matched city air quality distribution. The framework also solves critical problems of early warning systems related to long-term sensor failure and prediction at a new location in the city."
    },
    {
        "title": "DID We Miss Anything?: Towards Privacy-Preserving Decentralized ID Architecture",
        "authors": [
            "Siwon Huh",
            "Myungkyu Shim",
            "Jihwan Lee",
            "Simon S. Woo",
            "Hyoungshick Kim",
            "Hojoon Lee"
        ],
        "venue_full": "IEEE Transactions on Dependable and Secure Computing",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            7.32
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/tdsc.2023.3235951"
        },
        "img": "TDSC.PNG",
        "abstract": "Decentralized Identity (DID) is emerging as a new digital identity management scheme that promises users complete control of their personal data and identification without central authority involvement. The World Wide Web Consortium (W3C) has drafted the DID standard and provided reference implementations. We conduct a security analysis of the W3C DID standard and the reference universal resolver implementation, focusing on user privacy in the DID resolving process. The universal resolver is the key component in the architecture that processes DID requests and DID document retrievals. Our analysis demonstrates that privacy issues can arise due to the imprudent design of the universal resolver. Furthermore, we found that side-channels in the DID document caching schemes of real-world DID services can entail privacy concerns. Motivated by our security analysis, we present a novel  DID resolving design, called Oblivira, to enable obliviously DID resolving. Oblivira is a secure resolving agent with a small footprint that enforces the universal resolver to resolve requests without knowing their content. We also propose a privacy-preserving DID document caching scheme that eliminates side-channels. Our evaluation results show that Oblivira only incurs approximately 2.6\\% of overhead on average with different resolver settings (3, 6, and 12 threads)."
    },
    {
        "title": "Evaluating Racial Bias in Face Recognition APIs using Deepfakes",
        "authors": [
            "Shahroz Tariq",
            "Sowon Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Computer Magazine",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.56
        ],
        "year": 2023,
        "links": {},
        "img": "/img/Publications/shahroz_ieee_computer.png",
        "abstract": "Deep learning algorithms enable rapid growth in web-based services such as natural language processing, speech recognition, and facial recognition. Simultaneously, online fairness and trust remain unresolved. For example, racial bias in web-based face recognition services can lead to inaccurate results, causing severe technical and social issues and widespread distrust in AI-based systems. Deepfake on social media has posed several credibility issues. We evaluate the racial bias in face recognition APIs using real and deepfake celebrity images. We use deepfake generation methods to introduce small, imperceptible changes to the real images to shift the racial class of predictions. As a result, we show how deepfake images exacerbated racial bias in Amazon, Microsoft, and Naver web-based face recognition APIs. The findings are significant because they reveal similar vulnerabilities to those previously discovered through adversarial attacks but through a significantly different method."
    },
    {
        "title": "Design and evaluation of highly accurate smart contract code vulnerability detection framework",
        "authors": [
            "Sowon Jeon",
            "Gilhee Lee",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Data Mining and Knowledge Discovery",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.67
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1007/s10618-023-00981-1"
        },
        "img": "sowon.JPG",
        "abstract": "In this paper, we present SmartConDetect as a tool for detecting security vulnerabilities in Solidity smart contracts. SmartConDetect is a static analysis tool that extracts code fragments from Solidity smart contracts and uses a pre-trained BERT model to find susceptible code patterns. To demonstrate the performance of SmartConDetect, we use two public datasets, and our dataset (SmartConDataset) collected from the real-world Ethereum blockchain network. Our experimental results show that SmartConDetect significantly outperforms all state-of-the-art methods, achieving 90.9\\% F1-score when using our own dataset. Specifically, SmartConDetect is about 2 times faster than SmartCheck in detection. Furthermore, we conduct a real-world case study to analyze the distribution of detected vulnerabilities."
    },
    {
        "title": "A-ColViT : Real-time Interactive Colorization by Adaptive Vision Transformer",
        "authors": [
            "Gwanghan Lee",
            "Saebyeol Shin",
            "Donggeun Ko",
            "Jiyeon Jung",
            "Simon S. Woo"
        ],
        "venue_full": "AAAI Workshop on Practical Deep Learning in the Wild",
        "venue": "PDLW",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {},
        "img": "/img/Publications/gwanhan_aaai23.jpg",
        "abstract": "Vision transformer has been used to alleviate this problem by using multi-head self attention to propagate user hints to distant relevant areas in the image. However, despite the success of vision transformers in colorizing the image and selectively colorizing the regions with user propagation hints, heavy underlying ViT architecture and the large number of required parameters hinder active real-time user interaction for colorization applications. Thus, in this work, we propose a novel efficient ViT architecture for real-time interactive colorization, A-ColViT that adaptively prunes the layers of vision transformer for every input sample. This method flexibly allocates computational resources of input samples, effectively achieving actual acceleration. In addition, we demonstrate through extensive experiments on ImageNet-ctest10k, Oxford 102flower, and CUB-200 datasets that our method outperforms the state-of-the-art approach and achieves actual acceleration."
    },
    {
        "title": "S-ViT: Sparse Vision Transformer for Accurate Face Recognition",
        "authors": [
            "Geunsu Kim",
            "Gyudo Park",
            "Soohyeok Kang",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3555776.3577640"
        },
        "img": "/img/Publications/kim_sac23.jpg",
        "abstract": "In this work, we propose a Sparse Vision Transformer (S-ViT) based on the Vision Transformer (ViT) architecture to improve the face recognition tasks. After the model is trained, S-ViT tends to have a sparse distribution of weights compared to ViT, so we named it according to these characteristics. Unlike the conventional ViT, our proposed S-ViT adopts image Relative Positional Encoding (iRPE) method for positional encoding. Also, S-ViT has been modified so that all token embeddings, not just class token, participate in the decoding process. Through extensive experiment, we showed that S-ViT achieves better performance in closed-set than the other baseline models, and showed better performance than the baseline ViT-based models. We also show that the use of ArcFace loss functions yields greater performance gains in S-ViT than in baseline models. In addition, S-ViT has an advantage in cost-performance trade-off because it tends to be more robust to the pruning technique than the underlying model, ViT. Therefore, S-ViT offers the additional advantage, which can be applied more flexibly in the target devices with limited resources."
    },
    {
        "title": "MGCMA: Multi-scale Generator with Channel-wise Mask Attention to generate Synthetic Contrast-enhanced Chest Computed Tomography",
        "authors": [
            "Jeongho Kim",
            "Yun-Gyoo Lee",
            "Donggeun Ko",
            "Taejune Kim",
            "Soo-Youn Ham",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3555776.3578618"
        },
        "img": "/img/Publications/jho_sac23.png",
        "abstract": "Medical images, including computed tomography (CT) assist doctors and physicians in diagnosing anatomic structures and various internal pathologies. In CT, intravenous contrast media is often applied, which are chemicals developed to aid in the characterization of pathology by enhancing the capabilities of an imaging modality to differentiate between different biological tissues. Especially, with the use of contrast media, thorough examinations of the patients can be possible. However, contrast media can have severe adverse and side effects such as hypersensitive reaction to generalized seizures. Yet, without contrast media, it is difficult to diagnose patients that have disorders in the internal organs. With the help of DNN models, especially generative adversarial network (GAN), contrast-enhanced CT (CECT) images can be synthetically generated from non-contrast CT (NCCT) images. GANs or autoencoder-based models have been proposed to generate contrast-enhanced CT images; however, the synthesized image does not fully reflect and have crucial spots where contrast has not been synthesized. Thus, in order to enhance the quality of the CECT image, we propose MGCMA, a multi-scale generator with a channel-wise mask attention module for generating synthetic CECT images from NCCT images. Our extensive experiments demonstrate that our model outperforms other baseline models in various metrics such as SSIM and LPIPS. Also, generated images from our approach achieve plausible outcomes from the domain experts' (e.g., physicians and radiologists) evaluations."
    },
    {
        "title": "Rotated-DETR: an End-to-End Transformer-based Oriented Object Detector for Aerial Images",
        "authors": [
            "Giljun Lee",
            "Jinbeom Kim",
            "Taejune Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1145/3555776.3577745"
        },
        "img": "/img/Publications/jb_sac23.png",
        "abstract": "Oriented object detection in aerial images is a challenging task due to the highly complex backgrounds and objects with arbitrary oriented and usually densely arranged. Existing oriented object detection methods adopt CNN-based methods, and they can be divided into three types: two-stage, one-stage, and anchor-free methods. All of them require non-maximum suppression (NMS) to eliminate the duplicated predictions. Recently, object detectors based on the transformer remove hand-designed components by directly solving set prediction problems via performing bipartite matching, and achieve state-of-the-art performances in general object detection. Motivated by this research, we propose a transformer-based oriented object detector named  Rotated DETR with oriented bounding boxes (OBBs) labeling. We embed the scoring network to reduce the tokens corresponding to the background. In addition, we apply a proposal generator and iterative proposal refinement in order to provide proposals with angle information to the transformer decoder. Rotated DETR achieves state-of-the-art performance on the single-stage and anchor-free oriented object detectors on DOTA, UCAS-AOD, and DIOR-R datasets with only 10\\% feature tokens. In the experiment, we show the effectiveness of the scoring network and iterative proposal refinement."
    },
    {
        "title": "An overhead-free region-based JPEG framework for task-driven image compression",
        "authors": [
            "Seonghye Jeong",
            "Seongmoon Jeong",
            "Simon S. Woo",
            "Jong Hwan Ko"
        ],
        "venue_full": "Pattern Recognition Letters",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            5.67
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1016/j.patrec.2022.11.020"
        },
        "img": "/img/Publications/jeong_prl.jpg",
        "abstract": "An increasing amount of captured images are streamed to a remote server or stored in a device for deep neural network (DNN) inference. In most cases, raw images are compressed with encoding algorithms such as JPEG to cope with resource limitations. However, the standard JPEG optimized for human visual systems may induce significant accuracy loss in DNN inference tasks. In addition, the standard JPEG compresses all regions in an image at the same quality level, while some areas may not contain valuable information for the target task. In this paper, we propose a target-driven JPEG compression framework that performs region-adaptive quantization of the DCT coefficients. The region-based quality map is generated from an end-to-end trainable neural network. In addition, we present a deep learning approach to remove the requirement of storing the overhead information induced by the region-based encoding process. Our framework can be easily implemented on devices with commonly used JPEG and also produce images that achieve a higher compression rate with minimum degradation of the classification accuracy."
    },
    {
        "title": "CFL-Net: Image Forgery Localization Using Contrastive Learning",
        "authors": [
            "Fahim Faisal Niloy",
            "Kishor Kumar Bhaumik",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF Winter Conference on Applications of Computer Vision",
        "venue": "WACV",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2023,
        "links": {
            "conf": "https://doi.org/10.1109/wacv56688.2023.00462"
        },
        "img": "/img/Publications/wacv22_kishor.png",
        "abstract": "Conventional forgery localizing methods usually rely on different forgery footprints such as JPEG artifacts, edge inconsistency, camera noise, etc., with cross-entropy loss to locate manipulated regions. However, these methods have the disadvantage of over-fitting and focusing on only a few specific forgery footprints. On the other hand, real-life manipulated images are generated via a wide variety of forgery operations and thus, leave behind a wide variety of forgery footprints. Therefore, we need a more general approach for image forgery localization that can work well on a variety of forgery conditions. A key assumption in underlying forged region localization is that there remains a difference of feature distribution between untampered and manipulated regions in each forged image sample, irrespective of the forgery type. In this paper, we aim to leverage this difference of feature distribution to aid in image forgery localization. Specifically, we use contrastive loss to learn mapping into a feature space where the features between untampered and manipulated regions are well-separated for each image. Also, our method has the advantage of localizing manipulated region without requiring any prior knowledge or assumption about the forgery type. We demonstrate that our work outperforms several existing methods on three benchmark image manipulation datasets."
    },
    {
        "title": "A Novel Transformer-based Approach for Rotated Object Detection in Aerial Images",
        "authors": [
            "Jinbeom Kim",
            "Giljun Lee",
            "Taejune Kim",
            "Simon S. Woo"
        ],
        "venue_full": "추계 공동학술대회",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "매우 복잡한 배경과 임의로 회전 되어있고 조밀하게 배열되어 잇는 객체로 인해 항공 이미지에서 회전된 객체를 탐지하는 것은 매우 어려운 작업이다. 기존의 회전 객체 탐지 기법들은 CNN 기반 방법론을 채택하고 있으며, 이들은 세가지 카테고리 two-stage, one-stage, 그리고 anchor-free로 분류할 수 있다. 이들 모두 중복된 예측을 제거하기 위해 비최대 억제(NMS)가 필요하다. 최근 transformer를 기반으로 한 객체 탐지 모델은 이분 매칭을 통해 set prediction proble을 직접 해결하여 수작업으로 설계된 구성 요소들을 제거하면서 일반적인 객체 탐지 분야에서 최첨단 성능을 달성하였다. 이 연구에 자극을 받아, 우리는 방향 경계 상자(OBB) 라벨을 사용하는 transformer 기반 모델인 Rotated DETR를 제안한다.또한 우리는 proposal generator와 iterative proposal refinement를 적용하여 transformer decoder에 각도 정보를 제공한다. Rotated DETR은 10%의 feature token 만으로 DOTA 데이터 세트의 one-stage와 anchor-free 모델들에서 최첨단 성능을 달성한다. 우리는 실험을 통해 scoring network와 iterative proposal refinement의 효과를 보여준다."
    },
    {
        "title": "Effective Deepfake Detection using Mask Attention",
        "authors": [
            "Saebyeol Shin",
            "Simon S. Woo"
        ],
        "venue_full": "추계 공동학술대회",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "다양한 딥페이크 데이터셋에 대한 최신 딥페이크 탐지 모델은 놀라운 성능을 달성했습니다. 그러나 대부분의 접근 방식은 각 딥페이크 입력 이미지가 서로다른 지역적인 부분에서 구별되는 특징을 가지고 있다는 사실을 활용하지 않습니다. 따라서 본 논문은 입력 이미지의 서로 다른 세부적인 부분에 동적으로 초점을 맞추고 실제 이미지와 딥페이크 이미지의 미묘하고 세부적인 차이를 이용하는 효과적인 딥페이크 탐지 방법인 MaskDF를 제안합니다. 특히 중요하지 않은 특성을 제거하여 입력의 귀중한 정보를 보존할 수 있는 학습 가능한 어텐션 마스크를 제안합니다. 입력 피쳐는 제안된 게이팅 함수를 통과하여 어텐션 마스크 벡터를 생성하므로 딥페이크 탐지에 영향을 미치는 중요한 특징을 결정할 수 있습니다. 우리의 방법은 입력 정보의 절반만 사용하여 DFDC 및 FaceForensics++ 데이터 세트에서 다른 기본 모델보다 더 나은 성능을 보여주었습니다."
    },
    {
        "title": "Analysis of Obfuscation of Deepfake Images in Differential Privacy Settings",
        "authors": [
            "Donggeun Ko",
            "Simon S. Woo"
        ],
        "venue_full": "추계 공동학술대회",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "소셜 미디어나 감시 시스템에서 매일 수많은 얼굴 사진과 개인 정보가 수집된다. 얼굴 정보를 포함한 소셜 미디어 사용자의 개인 정보는 간단한 거래나 공항 출입국 절차의 간소화와 같은 이점이 있지만 이러한 이점은 항상 개인 정보 보호 문제를 수반한다. 위와 같은 민감한 정보들은 잠재적으로 유해한 목적으로 사용될 위험이 있기때문에 공격자에게 취약하다고 할 수 있다. 이러한 정보를 보호하기 위해 이미지의 프라이버시를 강화하는 솔루션인 DP(Differential Privacy)를 사용하여 높은 수준의 프라이버시를 제공한다. DP(Differential Privacy)를 통해 이미지의 프라이버시가 증가할 수 있지만 이상적인 epsilon-DP를 달성하기 위해서 유틸리티와 프라이버시 사이에는 필연적인 trade-off가 있다. 따라서 난독화 이미지의 최적 매개변수를 선택하는 것이 개인정보 보호의 핵심이며 본 논문에서는 이미지의 프라이버시를 강화하기 위해 각각 DP-Pix, DP-SVD, Snow라는 3가지 DP(Differential Privacy) 난독화 방법을 제시한다. 또한 딥 러닝 모델의 견고성을 평가하는 딥페이크 이미지 데이터셋에서 DP 방법을 구현하는 다양한 방법을 시연한다. 실험의 결과는 훈련 단계에서 데이터 세트 증대가 epsilon-DP(Differential Privacy를 사용하여 딥페이크를 탐지할 때 모델의 성능을 쉽게 향상시킬 수 있음을 나타낸다."
    },
    {
        "title": "Evaluation of Deepfakes with Generated Facemasks",
        "authors": [
            "Donggeun Ko",
            "Simon S. Woo"
        ],
        "venue_full": "추계 공동학술대회",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "최근들어 딥페이크(Deepfake) 기술의 발전으로 인해 국제사회의 우려가 점점 커지고 있다. 딥페이크 기술은 이미지나 영상 속 얼굴을 손쉽게 생성, 조작하여 왜곡된 정보를 전파할 수 있기 때문이다. 이에 따라 최첨단 성능을 갖춘 다양한 딥페이크 탐지 모델이 제안되어 왔다. 그러나 지금까지 제안된 딥페이크 탐지 모델은 펜데믹 위기 동안 발생했을 마스크가 착용된 얼굴에 대한 정보는 고려하지 않고 있다. 마스크가 착용된 얼굴 이미지의 경우 얼굴의 중요한 랜드마크가 마스크 속에 숨겨져 있기 때문에 딥페이크 탐지기의 성능을 보장하기 어렵다. 따라서 본 논문에서는 이러한 문제를 해결할 수 있는 두 가지 간단한 방법론을 제시하고 기존 방법론들과의 비교실험을 통해 마스크가 착용된 얼굴 이미지와 마스크가 착용되지 않은 얼굴 이미지 사이에서 나타날 수 있는 딥페이크 탐지 모델의 문제점과 제시된 방법론의 효과를 살펴보고자 한다."
    },
    {
        "title": "RCRL: Replay-based Continual Representation Learning in Multi-task Super-Resolution",
        "authors": [
            "Jinyong Park",
            "Minha Kim",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE International Conference on Advanced Video and Signal Based Surveillance",
        "venue": "AVSS",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1109/avss56176.2022.9959552"
        },
        "img": "/img/Publications/jinyong_rcrl.png",
        "abstract": "Super-resolution (SR) aims to recover the highresolution (HR) images from low-resolution (LR) images. Recently, various attempts, e.g., unsupervised SR models and domain-specific SR have achieved outstanding performance for various real-world applications. However, they significantly suffer from low generalization performance when trained on another domain dataset. Furthermore, they often exhibit performance degradation when the model continually learns multiple tasks; so-called catastrophic forgetting degrades the SR performance. In this paper, we are the first to propose a novel approach for continual multi-task SR named Replay-based Continual Representation Learning framework that can be applicable to GAN-based SR models, which utilizes feature memory for preserving the learned features from the previous task. Our experimental results demonstrate the effectiveness of RCRL in continual multi-task SR at improving generalization performance and alleviating catastrophic forgetting."
    },
    {
        "title": "STL-DP: Differentially Private Time Series Exploring Decomposition and Compression Methods",
        "authors": [
            "Kyunghee Kim",
            "Minha Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM CIKM Workshop on Privacy Algorithms in Systems",
        "venue": "PAS",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": "/img/Publications/cikmw22_minha.png",
        "abstract": "As time series data is collected and used in a variety of fields, the importance of preserving privacy on time series is also on the increase. This paper is a preliminary study of the Differential Privacy (DP) algorithm specially designed to provide privacy to time series data by integrating the time series decomposition technique. In particular, this study extends the Fourier Perturbation Algorithm (FPA) with Seasonal and Trend decomposition using LOESS (STL). In this work, we propose STL-DP, which first performs STL decomposition to the original data. Then we apply the FPA only to the core part of the time series, particularly trend or seasonal components, to provide privacy. In this preliminary study, we show that our approach consistently outperforms other baselines in terms of utility according to the experimental results."
    },
    {
        "title": "A<sup>2</sup>: Adaptive Augmentation for Mitigating Dataset Bias",
        "authors": [
            "Jaeju An",
            "Taejun Kim",
            "Donggeun Ko",
            "Sangyup Lee",
            "Simon S. Woo"
        ],
        "venue_full": "Asian Conference on Computer Vision",
        "venue": "ACCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2022,
        "links": {},
        "img": "/img/Publications/accv22_jaeju.png",
        "abstract": "The trained networks can often suffer from overfitting issues due to the unintended bias in a dataset causing inaccurate, unreliable, and untrustworthy results. To tackle this problem, we propose a novel augmentation framework, Adaptive Augmentation (A^2), based on a generative model and few-shot adaptation for augmenting bias-conflict samples that help classifiers learn debiased representations without any prior knowledge about bias types. Our framework consists of three steps: 1) extracting bias-conflict samples from a biased dataset in an unsupervised manner, 2) training a generative model with the biased dataset and adapting biased distribution from the generative model to the extracted bias-conflict samples' distribution, and 3) augmenting bias-conflict samples by translating bias-align samples with the trained generative model. Therefore, our classifier can effectively learn the debiased representation without human supervision."
    },
    {
        "title": "Discussion about Attacks and Defenses for Fair and Robust Recommendation System Design",
        "authors": [
            "Mirae Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM RecSys Workshop on Responsible Recommendation",
        "venue": "FAccTRec",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2210.07817"
        },
        "img": "/img/Publications/facctrec_mirae22.png",
        "abstract": "Information has exploded on the Internet and mobile with the advent of the big data era. In particular, recommendation systems are widely used to help consumers who struggle to select the best products among such a large amount of information. However, recommendation systems are vulnerable to malicious user biases, such as fake reviews to promote or demote specific products, as well as attacks that steal personal information. Such biases and attacks compromise the fairness of the recommendation model and infringe the privacy of users and systems by distorting data.Recently, deep-learning collaborative filtering recommendation systems have shown to be more vulnerable to this bias. In this position paper, we examine the effects of bias that cause various ethical and social issues, and discuss the need for designing the robust recommendation system for fairness and stability."
    },
    {
        "title": "Accelerating CNN via Dynamic Pattern-based Pruning Network",
        "authors": [
            "Gwanghan Lee",
            "Saebyeol Shin",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3511808.3557225"
        },
        "img": "/img/Publications/cikm22_gwanhan.png",
        "abstract": "Most dynamic pruning methods fail to achieve actual acceleration due to the extra overheads caused by indexing and weight-copying to implement the dynamic sparse patterns for every input sample. To address this issue, we propose Dynamic Pattern-based Pruning Network, which preserves the advantages of both static and dynamic networks. Unlike previous dynamic pruning methods, our novel method dynamically fuses static kernel patterns, enhancing the kernel's representational power without additional overhead. Moreover, our dynamic sparse pattern enables an efficient process using BLAS libraries, accomplishing actual acceleration. We demonstrate the effectiveness of the proposed network on CIFAR and ImageNet, outperforming the state-of-the-art methods achieving better accuracy with lower computational cost."
    },
    {
        "title": "Samba: Identifying Inappropriate Videos for Young Children on YouTube",
        "authors": [
            "Binh M. Le",
            "Rajat Tandon",
            "Chingis Oinar",
            "Jeffrey Liu",
            "Uma Durairaj",
            "Jiani Guo",
            "Spencer Zahabizadeh",
            "Sanjana Ilango",
            "Jeremy Tang",
            "Fred Morstatter",
            "Simon S. Woo",
            "Jelena Mirkovic"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2022,
        "links": {},
        "img": "/img/Publications/cikm22_binh.png",
        "abstract": "In this paper, we propose a fusion model, called Samba, which uses both metadata and video subtitles for content classifying YouTube videos for kids. Previous studies utilized metadata, such as video thumbnails, title, comments, ect., for detecting inappropriate videos for young viewers.  Such metadata-based approaches achieve high accuracy but still have significant misclassifications due to the reliability of input features. By adding representation features from subtitles, which are pretrained with a self-supervised contrastive framework, our Samba model can outperform other state-of-the-art classifiers by at least 7%. We also publish a large-scale, comprehensive dataset of 70K videos for future studies."
    },
    {
        "title": "Towards an Awareness of Time Series Anomaly Detection Models' Adversarial Vulnerability",
        "authors": [
            "Shahroz Tariq",
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3511808.3557073"
        },
        "img": "/img/Publications/cikm22_shah.png",
        "abstract": "Time series anomaly detection is studied in statistics, ecology, and computer science. Numerous time series anomaly detection strategies have been presented utilizing deep learning. Many of these methods exhibit state-of-the-art performance on benchmark datasets, giving the false impression that they are robust and deployable in a wide variety of real-world scenarios. In this study, we demonstrate that adding modest adversarial perturbations to sensor data severely weakens anomaly detection systems.   Under well-known adversarial attacks such as Fast Gradient Sign Method (FGSM) and Projected Gradient Descent (PGD), we demonstrate that the performance of state-of-the-art deep neural networks (DNNs) and graph neural networks (GNNs), which claim to be robust against anomalies and possibly be used in real-world systems, drops to 0%. We demonstrate for the first time, to our knowledge, the vulnerability of anomaly detection systems to adversarial attacks. This study aims to increase awareness of the adversarial vulnerabilities of time series anomaly detectors."
    },
    {
        "title": "Sliding Cross Entropy for Self-Knowledge Distillation",
        "authors": [
            "Hanbeen Lee",
            "Jeongho Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3511808.3557453"
        },
        "img": "/img/Publications/cikm22_hanbeen.png",
        "abstract": "Knowledge distillation (KD) is a powerful technique for improving the performance of a small model by leveraging the knowledge of a larger model. Despite its remarkable performance boost, KD has a drawback with the substantial computational cost of pre-training larger models in advance. Recently, a method called self-knowledge distillation has emerged to improve the model's performance without any supervision. In this paper, we present a novel plug-in approach called Sliding Cross Entropy (SCE) method, which can be combined with existing self-knowledge distillation to significantly improve the performance. Specifically, to minimize the difference between the output of the model and the soft target obtained by self-distillation, we split each softmax representation by a certain window size, and reduce the distance between sliced parts. Through this approach, the model evenly considers all the inter-class relationships of a soft target during optimization. The extensive experiments show that our approach is effective in various tasks, including classification, object detection, and semantic segmentation. We also demonstrate SCE consistently outperforms existing baseline methods."
    },
    {
        "title": "Selective Tensorized Multi-layer LSTM for Orbit Prediction",
        "authors": [
            "Youjin Shin",
            "Eun-Ju Park",
            "Simon S. Woo",
            "Okchul Jung",
            "Daewon Chung"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3511808.3557138"
        },
        "img": "/img/Publications/cikm22_youjin.png",
        "abstract": "Although the collision of space objects not only incurs a high cost but also threatens human life, the risk of collision between satellites has increased, as the number of satellites has rapidly grown due to the significant interests in many space applications. However, it is not trivial to monitor the behavior of the satellite in real-time since the communication between the ground station and spacecraft are dynamic and sparse, and there is an increased latency due to the long distance. Accordingly, it is strongly required to predict the orbit of a satellite to prevent unexpected contingencies such as a collision. Therefore, the real-time monitoring and accurate orbit prediction is required. Furthermore, it is necessarily to compress the prediction model, while achieving a high prediction performance in order to be deployable in the real systems. Although several machine learning and deep learning-based prediction approaches have been studied to address such issues, most of them have applied only basic machine learning models for orbit prediction without considering the size, running time, and complexity of the prediction model. In this research, we propose Selective Tensorized multi-layer LSTM (ST-LSTM) for orbit prediction, which not only improves the orbit prediction performance but also compresses the size of the model that can be applied in practical deployable scenarios. To evaluate our model, we use the real orbit dataset collected from the Korea Multi-Purpose Satellites (KOMPSAT-3 and KOMPSAT-3A) of the Korea Aerospace Research Institute (KARI) for 5 years. In addition, we compare our ST-LSTM to other machine learning-based regression models, LSTM, and basic tensorized LSTM models with regard to the prediction performance, model compression rate, and running time."
    },
    {
        "title": "GLAMD: Global and Local Attention Mask Distillation for Object Detectors",
        "authors": [
            "Younho Jang",
            "Wheemyung Shin",
            "Jinbeom Kim",
            "Simon S. Woo",
            "Sung-Ho Bae"
        ],
        "venue_full": "European Conference on Computer Vision",
        "venue": "ECCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-031-20080-9_27"
        },
        "img": "/img/Publications/jinpum_eccv22.png",
        "abstract": "Knowledge distillation (KD) is a well-known model compression strategy to improve models' performance with fewer parameters. However, recent KD approaches for object detection have faced two limitations. First, they distill nearby foreground regions, ignoring potentially useful background information. Second, they only consider global contexts, thereby the student model can hardly learn local details from the teacher model. To overcome such challenging issues, we propose a novel knowledge distillation method, GLAMD, distilling both global and local knowledge from the teacher. We divide the feature maps into several patches and apply an attention mechanism for both the entire feature area and each patch to extract the global context as well as local details simultaneously. Our method outperforms the state-of-the-art methods with 40.8 AP on COCO2017 dataset, which is 3.4 AP higher than the student model (ResNet50 based Faster R-CNN) and 0.7 AP higher than the previous global attention-based distillation method."
    },
    {
        "title": "다중 스케일 특성 생성 네트워크",
        "authors": [
            "Gwanghan Lee",
            "Saebyeol Shin",
            "Simon S. Woo"
        ],
        "venue_full": "한국컴퓨터종합학술대회",
        "venue": "KCC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "조기 종료 네트워크(early-exit network)는 추론 시 동적으로 모델 복잡도를 낮춤으로써 신경망의 효율성을 높인다. 기존 연구들은 입력 샘플이나 모델 구조의 중복성(redundancy)을 줄이는 데 집중하였으나 고차원 특징 정보가 부족한 초기 분류기들이 전체 네트워크 성능에 치명적인 영향을 끼치는 문제를 해결하지 못했다. 본 연구는 중복성을 줄이는 것뿐만 아니라 합성곱 커널(convolution kernel) 중앙에서 가중치들을 공유하면서 효율적으로 다중 스케일(multi-scale) 특징을 생성하여 조기 종료 네트워크의 성능을 향상시킨다. 또한 이 논문의 게이팅 네트워크(gating network)는 네트워크의 서로 다른 위치에 있는 각 합성곱 레이어에 따라 최적의 다중 스케일 특징 비율을 결정하도록 학습된다."
    },
    {
        "title": "이미지 전처리 방법을 통한 딥페이크 탐지 회피 연구",
        "authors": [
            "Jeongho Kim",
            "Jeonghyun Kim",
            "Taejune Kim",
            "Simon S. Woo"
        ],
        "venue_full": "한국컴퓨터종합학술대회",
        "venue": "KCC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "오늘날 국제사회에서 딥페이크(Deepfake) 기술에 대한 우려가 점점 커지고 있다. 딥페이크는 여러 종류의 이미지, 영상들의 얼굴을 짧은 시간 만에 바꿀 수 있는 기술로, 손쉽게 왜곡된 정보를 전파할 수 있기 때문이다. 이에따라딥페이크이미지,영상에대응하기위한탐지기술연구및시도가이뤄졌다. 그러나,탐지기술연구를 가능케 만들어 줄 수 있는 고품질의 데이터셋(dataset)을 생성하는 연구는 더디게 이뤄졌다. 본 논문에서는 딥페 이크 탐지 기술 발전에 필수 불가결한 요소인 고품질 데이터 생성에 대한 새로운 방법론을 제시하고 이를 통해 딥페이크 탐지 기술의 한계 및 발전 방향성에 대해 살펴보고자 한다."
    },
    {
        "title": "Deep Learning Algorithm for Postmortem Face Reconstruction (딥러닝 기술을 활용한 사후 시신 얼굴 복원)",
        "authors": [
            "Hajin Kim",
            "Chingis Oinar",
            "UiHyeon Shin",
            "Woo Simon S",
            "Moon-Young Kim"
        ],
        "venue_full": "제29회 대한기초의학 학술대회",
        "venue": "대한법의학회",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {},
        "img": "dead.JPG",
        "abstract": "As the number of lonely deaths increases due to the aging population and the increase in single-person households, the frequency of discovery of decomposed corpses in death cases is gradually increasing. In the wake of the strengthening of on-site guidelines by the National Police Agency and the adjustment of the prosecution and police investigation rights, the need for identification and autopsy at the scene is being emphasized. Although the existing forensic face restoration technology using face bones has accumulated a number of previous studies, there is a limitation in that the restoration results may vary due to many factors such as the thickness and nature of facial soft tissue, shape of eyes or nose, and distribution of body hair. Based on the fact that facial recognition technology using facial landmarks is becoming common all over the world, this study aims to help quickly and accurately identify the faces of corrupt bodies that expand due to postmortem-change.\nIn this study, living data such as ID cards and post-mortem data were collected for bodies identified with fingerprints, and compared pairs were formed, and face recognition technology used the MTCNN model, which is currently widely used in the field. The artificial intelligence model, which determines whether live data and post-data match, selected and analyzed Arcface, which is the same among a total of seven open-source models (VGG-Face, FaceNet, OpenFace, DeepFace, DeepID, ArcFace, Dlib).\nThe performance of the artificial intelligence model (Arcface) was evaluated by comparing the results of the judgment of the expert group, the general public group, and the entire human group. As a result of comparison using 107 pairs of original data, the same person judgment rate was found to be 51.4% in the expert group, 22.4% in the general population, and 29.0% in the total human group, and the artificial intelligence model was 47.7%. As a result of reviewing the original data, it was determined that changes in skin color due to decomposition could affect the performance of artificial intelligence models According to this judgment, when the original data were preprocessed in gray scale, the judgment rate of the same person as the artificial intelligence model was 50.5%, which showed an improvement in performance of about 3%. \nThrough this study, it was found that only the currently developed artificial intelligence model showed facial recognition performance close to that of a group of experts. It is expected that face recognition performance can be further improved if various pretreatment technologies reflecting the characteristics of the postmortem change are developed and applied in the future.\n인구 고령화 및 1인 가구의 증가는 고독사의 증가로 이어져 변사사건에서 부패 시신이 발견되는 빈도가 점차 높아지고 있다. 경찰청의 현장 지침 강화 및 검경 수사권 조정 등을 계기로 현장에서는 신원 확인 및 부검의 필요성이 강조되고 있다. 얼굴뼈를 활용한 기존의 법의학적 얼굴 복원 기술은 다수의 선행연구 결과가 축적되어 있지만, 얼굴 연부조직의 두께나 성상, 눈이나 코의 형태, 체모의 분포 등의 고려 요소가 많아 복원 결과가 달라질 수 있다는 한계가 존재한다. 본 연구는 얼굴의 특징점(face landmark)을 활용하는 얼굴 인식 기술이 전세계적으로 보편화되고 있다는 점에 착안하여, 사후변화로 인해 연부조직이 팽창된 부패 시신의 얼굴을 복원하거나 생전의 사진과 비교하여 동일인 여부를 판정함으로써 신속하고 정확한 신원확인에 도움을 주고자 한다. \n 본 연구에서는 지문 등으로 신원이 확인된 시신을 대상으로 신분증 등의 생전 데이터와 검안 또는 부검 당시 촬영된 사후데이터를 수집한 뒤 각각 짝을 지어 비교쌍을 구성하였으며, 얼굴 인식 기술은 현재 해당 분야에서 많이 활용되고 있는 MTCNN 모델을 활용하였다. 생전데이터와 사후데이터의 일치 여부를 판단하는 인공지능모델은 총 7개의 open source 모델(VGG-Face, FaceNet, OpenFace, DeepFace, DeepID, ArcFace, Dlib) 중 가장 동일인 판정률의 빈도가 가장 높게 나타난 Arcface를 선정하여 분석하였다.\n 인공지능모델(Arcface)의 성능은 전문가집단과 일반인 집단, 전체 사람 집단의 판정 결과와 비교하여 평가하였다. 원본 데이터 107쌍을 이용한 비교 결과, 동일인 판정률은 전문가집단 51.4%, 일반인 22.4%, 전체 사람 집단 29.0%로 조사되었으며, 인공지능모델은 47.7%로 나타났다. 원본 데이터를 검토한 결과, 부패로 인한 피부색의 변화가 인공지능모델의 성능에 영향을 줄 가능성이 있다고 판단되었다. 이러한 판단에 따라 원본 데이터를 회색조(gray scale)로 전처리하였을 때 인공지능모델의 동일인 판정률은 50.5%로, 약 3%의 성능이 향상되는 것을 볼 수 있었다. \n본 연구를 통해 현재 개발되어 있는 인공지능모델만으로도 전문가 집단에 근접한 얼굴 인식 성능을 보이는 것을 알 수 있었다. 향후 사후변화의 특성을 반영한 다양한 전처리 기법을 개발하여 적용할 경우 얼굴 인식 성능을 더욱 향상시킬 수 있을 것으로 기대된다."
    },
    {
        "title": "Learning Sparse Latent Graph Representations for Anomaly Detection in Multivariate Time Series",
        "authors": [
            "Siho Han",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "venue": "KDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3534678.3539117"
        },
        "img": "/img/Publications/kdd22_sean.png",
        "abstract": "Anomaly detection in high-dimensional time series is typically tackled using either reconstruction- or forecasting-based deep learning algorithms. Both streams of approach have seen enormous success in terms of detection accuracy due to their abilities to learn compressed data representations and model temporal dependencies, respectively. However, most existing methods disregard the relationships between features, information that would be extremely useful when incorporated into the model. How can we effectively combine the best of reconstruction and forecasting models while also capturing feature interdependencies? In this work, we introduce Fused Sparse Autoencoder and Graph Net (FuSAGNet), which jointly optimizes reconstruction and forecasting while explicitly modeling the relationships within multivariate time series. Our approach combines Sparse Autoencoder and Graph Neural Network, the latter of which predicts future time series behavior from sparse latent representations learned by the former as well as graph structures learned through recurrent feature embedding. Experimenting on three real-world cyber-physical system datasets, we empirically demonstrate that the proposed method enhances the overall anomaly detection performance, outperforming baseline approaches. Moreover, we show that mining sparse latent patterns from high-dimensional time series improves the robustness of the graph-based forecasting model. Lastly, we conduct visual analyses to investigate the interpretability of both recurrent feature embedding vectors and sparse latent representations."
    },
    {
        "title": "Evading Deepfake Detectors via High Quality Face Pre-Processing Methods",
        "authors": [
            "Jeongho Kim",
            "Taejune Kim",
            "Jeonghyeon Kim",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Pattern Recognition",
        "venue": "ICPR",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1109/icpr56361.2022.9956520"
        },
        "img": "/img/Publications/ICPR_2022_Evading_deepfake.png",
        "abstract": "Today, various multimedia content can be accessed and shared from any location via the Internet. In addition to normal content, there is an extensive amount of manipulated multimedia that can raise various social issues and concerns. Among the various types of manipulated media, deepfakes can be abused in impersonation or spreading fake information. Therefore, numerous studies have been performed to detect deepfakes to alleviate these concerns, and studies such as FaceForensics++ (FF++) and DeepFake Detection Challenge (DFDC) have sparked these studies by providing deepfake datasets. The deepfake datasets were utilized for supervised learning in conjunction with developing sophisticated neural networks and showed a high detection performance. Since powerful neural networks can learn even subtle details about an image, they must be trained on realistic deepfakes created by advanced deepfake generation technologies to improve the robustness of existing detectors. In order to boost the performance of deepfake detection models, we propose an approach to creating more realistic deepfake images by removing \"detectable\" artifacts from existing deepfake datasets' images. By applying the proposed method to the original deepfake dataset, we demonstrate that our technique can significantly reduce the detection performance of existing deepfake detectors. Our experimental results show the vulnerability of deployed detectors and pave the way for further improvement."
    },
    {
        "title": "Efficient Two-stage Model Retraining for Machine Unlearning",
        "authors": [
            "Junyaup Kim",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on Human-centered Intelligent Services: Safe and Trustworthy",
        "venue": "HCIS",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1109/cvprw56347.2022.00482"
        },
        "img": "/img/Publications/junjyuap_cvprw22.png",
        "abstract": "With the rise of the General Data Protection Regulation (GDPR), user data holders should guarantee the “individual’s right to be forgotten”. It means user data holders must completely remove user data when they receive the request. However, enabling a deep learning model to exclude specific data used during training is challenging. We can’t define what is ”forgetting” in deep learning and how to do it. To address this issue, we propose an efficient machine unlearning architecture to be used for computer vision classification models. Our approach consists of two-stage, where in the first stage we render a deep learning model that loses information with contrastive labels in the requested dataset. Second, we retrain the first stage output model with knowledge distillation (KD). Using this two-stage approach, we can substantiate the removal or forgetness of the requested dataset in the deep learning model. With various datasets used for multimedia applications, we demonstrate that our approach achieves performance on par or even higher accuracy than the original model, while effectively removing the requested data."
    },
    {
        "title": "Negative Adversarial Example Generation Against Naver's Celebrity Recognition API",
        "authors": [
            "Keeyoung Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3494109.3527193"
        },
        "img": "/img/Publications/wdc_kim.png",
        "abstract": "Deep Neural Networks (DNNs) are very effective in image classification, detection and recognition due to a large number of available data. However, they can be easily fooled by adversarial examples and produce incorrect results, which can cause problems for many applications. In this work, we focus on generating adversarial images and exploring and assessing possible negative impacts caused by these examples. As a case study, we create adversarial images against Naver’s celebrity recognition (NCR) API, as Naver is the leading machine learning APIs service provider in South Korea. We demonstrate that it is extremely easy to fool the online DNN-based APIs using adversarial examples and discuss possibe negative impacts resulting from these adversarial examples."
    },
    {
        "title": "A Face Pre-Processing Approach to Evade Deepfake Detector",
        "authors": [
            "Taejune Kim",
            "Jeongho Kim",
            "Jeonghyeon Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3494109.3527190"
        },
        "img": "/img/Publications/wdc2_taejune.png",
        "abstract": "Recently, various image synthesis technologies have increased the prevalence of impersonation attacks, and with the development of such technologies, the amount of damage such as defamation has also increased. Deepfake, the representative of the impersonation technique, has already evolved to the point where people cannot distinguish, leading to an urgent need for detection methods. Currently, in order to detect deepfakes, many deepfake datasets are widely used in deep neural networks using supervision learning. However, although this method is robust to the images synthesized by deepfake generation methods already known, it remains undefined whether deepfakes created by unknown techniques can be detected. Accordingly, to detect more challenging deepfakes, we present a pre-processing technique that mitigates the artifacts of deepfakes and makes them appear more natural. The proposed method can be combined with the existing deepfake creation method to generate a more threatening deepfake image. Furthermore, through extensive experiments, we demonstrate that our method can significantly lower the performance of state-of-the-art detectors and expose the vulnerability of deployed detectors."
    },
    {
        "title": "Deepfake Detection for Fake Images with Facemasks",
        "authors": [
            "Sangjun Lee",
            "Donggeun Ko",
            "Jinyong Park",
            "Saebyeol Shin",
            "Donghee Hong",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3494109.3527189"
        },
        "img": null,
        "abstract": "Hyper-realistic face image generation and manipulation have givenrise to numerous unethical social issues, e.g., invasion of privacy,threat of security, and malicious political maneuvering, which re-sulted in the development of recent deepfake detection methodswith the rising demands of deepfake forensics. Proposed deepfakedetection methods to date have shown remarkable detection perfor-mance and robustness. However, none of the suggested deepfakedetection methods assessed the performance of deepfakes withthe facemask during the pandemic crisis after the outbreak of theCovid-19. In this paper, we thoroughly evaluate the performance ofstate-of-the-art deepfake detection models on the deepfakes withthe facemask. Also, we propose two approaches to enhance themasked deepfakes detection:face-patchandface-crop. The experi-mental evaluations on both methods are assessed through the base-line deepfake detection models on the various deepfake datasets.Our extensive experiments show that, among the two methods,face-cropperforms better than theface-patch, and could be a trainmethod for deepfake detection models to detect fake faces withfacemask in real world."
    },
    {
        "title": "Zoom-DF: A Dataset for Video Conferencing Deepfake",
        "authors": [
            "Geon-Woo Park",
            "Eun-Ju Park",
            "Simon S. Woo"
        ],
        "venue_full": "ACM ASIACCS Workshop on Security Implications of Deepfakes and Cheapfakes",
        "venue": "WDC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3494109.3527195"
        },
        "img": "/img/Publications/wdc22_deonwoo.png",
        "abstract": "With the growth of deep learning studies, the technologies of generating deepfake videos have been advanced. While the manipulated videos are so sophisticated that one cannot differentiate between real and fake, one can create such videos with little effort. These technologies are likely to be abused by people with malicious intent. To address the problem, the algorithms for detecting deepfakes have been researched abundantly. The performance of the detectors, however, depends on the amount and the domain of the training data. In this paper, we introduce a new deepfake dataset generated by an algorithm changing an original image to a sequence of fake images. We evaluate existing models detecting deepfakes on the new dataset and demonstrate that the accuracy of the models degrades. Their performance is recovered when trained with the new dataset."
    },
    {
        "title": "PasswordTensor: Analyzing and explaining password strength using tensor decomposition",
        "authors": [
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "Computers & Security",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            4.4
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1016/j.cose.2022.102634"
        },
        "img": "/img/Publications/computer_security_2022_yj.png",
        "abstract": "A textual password is widely used for user authentication for a variety of applications. Passwords that are easy to remember are also easy to be guessed, while complex and long passwords that provide strong security are difficult to remember. Also, there has been limited quantitative research to understand the factors that make passwords strong. In this research, we aim to expand our understanding of passwords through the lenses of data-driven analysis by characterizing a large number of password datasets with four different hypotheses. In particular, we use the tensor decomposition method that is effective in analyzing unlabeled high dimensional data. We first obtain 362,805 passwords from four different leaked password datasets. Next, we generate syntactic and semantic features for each password, then classify it into three strength groups using a statistical guessing attack model. Finally, we construct a 3rd-order password tensor and decompose it using the PARAFAC2 algorithm to examine the main characteristics which make passwords strong."
    },
    {
        "title": "A Survey of Deep Learning-Based Object Detection Methods and Datasets for Overhead Imagery",
        "authors": [
            "Junhyung Kang",
            "Shahroz Tariq",
            "Han Oh",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            0
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1109/access.2022.3149052"
        },
        "img": "/img/Publications/ieee_access_junhyung.png",
        "abstract": "Although extensive studies in deep learning-based object detection have achieved remarkable performance and success, they are still ineffective yielding a low detection performance, due to the underlying difficulties in overhead images. Thus, high-performing object detection in overhead images is an active research field to overcome such difficulties. This survey paper provides a comprehensive overview and comparative reviews on the most up-to-date deep learning-based object detection in overhead images. Especially, our work can shed light on capturing the most recent advancements of object detection methods in overhead images and the introduction of overhead datasets that have not been comprehensively surveyed before."
    },
    {
        "title": "Am I a Real or Fake Celebrity? Evaluating Face Recognition and Verification APIs under Deepfake Impersonation Attack",
        "authors": [
            "Shahroz Tariq",
            "Sowon Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3485447.3512212"
        },
        "img": "/img/Publications/www22_shah.png",
        "abstract": "Recent advancements in web-based multimedia technologies, such as face recognition web services powered by deep learning, have been significant. However, such technologies face persistent threats, as virtually anyone with access to deepfakes can quickly launch impersonation attacks, which pose a serious threat to authentication services. Despite its gravity, deepfake abuse involving commercial web services have not been investigated. Thus, we examine the robustness of black-box commercial face recognition web APIs (Microsoft, Amazon, Naver, and Face++) and open-source tools (VGGFace and ArcFace) against Deepfake Impersonation (DI) attacks. We demonstrate the vulnerability of face recognition technologies to DI attacks, achieving respective success rates of 78.0% for targeted (TA) attacks; we also propose mitigation strategies, lowering respective attack success rates to as low as 1.26% for TA attacks with adversarial training."
    },
    {
        "title": "BZNet: Unsupervised Multi-scale Branch Zooming Network for Detecting Low-quality Deepfake Videos",
        "authors": [
            "Sangyup Lee",
            "Jaeju An",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1145/3485447.3512245"
        },
        "img": "/img/Publications/www22_jaeju.png",
        "abstract": "Generating a deep learning-based fake video has become no longer rocket science. The advancement of automated Deepfake (DF) generation tools that mimic certain targets has rendered society vulnerable to fake news or misinformation propagation. In real-world scenarios, DF videos are compressed to low-quality (LQ) videos, taking up less storage space and facilitating dissemination through the web and social media. Such LQ DF videos are much more challenging to detect than high-quality (HQ) DF videos. To address this challenge, we rethink the design of standard deep learning-based DF detectors, specifically exploiting feature extraction to enhance the features of LQ images. We propose a novel LQ DF detection architecture, multi-scale Branch Zooming Network (BZNet), which adopts an unsupervised super-resolution (SR) technique and utilizes multi-scale images for training. We train our BZNet only using highly compressed LQ images and experiment under a realistic setting, where HQ training data are not readily accessible. Extensive experiments on the FaceForensics++ LQ and GAN-generated datasets demonstrate that our BZNet architecture improves the detection accuracy of existing CNN-based classifiers by 4.21\\% on average. Furthermore, we evaluate our method against a real-world Deepfake-in-the-Wild dataset collected from the internet, which contains 200 videos featuring 50 celebrities worldwide, outperforming the state-of-the-art methods by 4.13%."
    },
    {
        "title": "Residual Size is Not Enough for Anomaly Detection: Improving Detection Performance using Residual Similarity in Multivariate Time Series",
        "authors": [
            "Jeong-Han Yun",
            "Jonguk Kim",
            "Won-Seok Hwang",
            "Young Geun Kim",
            "Simon S. Woo",
            "Byung-Gil Min"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2022,
        "links": {},
        "img": null,
        "abstract": "Unsupervised anomaly detection is commonly performed by identifying unusual data samples (or anomalies) from the residual size produced by machine learning algorithms based on normal data (e.g., the residuals of regression models or reconstruction errors of autoencoder models), assuming that anomalies cause large residuals. Unfortunately, anomalies do not always cause large residuals. Anomaly detection algorithms based on residual size can miss anomalies that cause only small or noisy residuals for each variable in a multivariate time-series. To overcome this issue, we propose \"neighbors to residuals\" (N2RE), a novel anomaly scoring function based on residual similarity using nearest neighbor distance (NND). Even if residuals of anomalies are small, they show patterns that are different from those of residuals of normal data. Using N2RE can improve anomaly detection performance and reduce the variation in anomaly detection performance due to threshold changes. Experiments with various models on three cyber-physical system datasets verify that N2RE can achieve 19% higher anomaly detection performance than previous approaches without changes to the models."
    },
    {
        "title": "PTD: Privacy-Preserving Human Face Processing Framework using Tensor Decomposition",
        "authors": [
            "Jeongho Kim",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2022,
        "links": {},
        "img": "/img/Publications/tensor.png",
        "abstract": "Training data may include personal information such as human faces, which requires anonymization to provide user privacy. However, after anonymization, the performance of the original machine learning (ML) model degrades due to the reduced or missing information. In this work, we introduce a novel privacy-preserving tensor decomposition (PTD) method to anonymize human faces. Further, we evaluate\nreal vs. fake human face detection task as a practical use case scenario. Our approach achieves high performance as well as training data efficiency, where the essence of our approach is based on tensor decomposition to ensure face data privacy. In particular, we demonstrate that the core tensor of Tucker decomposition generated from the original face input can effectively represent the underlying characteristics of the original face data; that is, learning only from the core tensors is sufficient for differentiating real human face images from deepfakes. Also, we show that the original human face inputs are anonymized and cannot be recovered from the core tensors under different attacker models from the randomized HOOI algorithm. Through extensive experiments and analysis, we demonstrate that our method can result in high detection performance comparable to those of popular anonymization methods. Therefore, we show that our work strikes the balance between privacy and performance through the novel use of tensor decomposition."
    },
    {
        "title": "ADD: Frequency Attention and Multi-View Based Knowledge Distillation to Detect Low-Quality Compressed Deepfake Images",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "AAAI Conference on Artificial Intelligence",
        "venue": "AAAI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1609/aaai.v36i1.19886"
        },
        "img": "/img/Publications/aaai22_binh.png",
        "abstract": "Despite significant advancements of deep learning-based forgery detectors for distinguishing manipulated deepfake images, most detection approaches suffer from moderate to significant performance degradation with low-quality compressed deepfake images.\nBecause of the limited information in low-quality images, detecting low-quality deepfake remains an important challenge. In this work, we apply frequency domain learning and optimal transport theory in knowledge distillation (KD) to specifically improve the detection of low-quality compressed deepfake images. We explore transfer learning capability in KD to enable a student network to learn discriminative features from low-quality images effectively. In particular, we propose the Attention-based Deepfake detection Distiller (ADD), which consists of two novel distillations: 1) frequency attention distillation that effectively retrieves the removed high-frequency components in the student network, and 2) multi-view attention distillation that creates multiple attention vectors by slicing the teacher’s and student’s tensors under different views to transfer the teacher tensor’s distribution to the student more efficiently. Our extensive experimental results demonstrate that our approach outperforms state-of-the-art baselines in detecting low-quality compressed deepfake images."
    },
    {
        "title": "ORVAE: One-Class Residual Variational Autoencoder for Voice Activity Detection in Noisy Environment",
        "authors": [
            "Hasam Khalid",
            "Shahroz Tariq",
            "TaeSoo Kim",
            "Jong Hwan Ko",
            "Simon S. Woo"
        ],
        "venue_full": "Neural Processing Letters",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            2.9
        ],
        "year": 2022,
        "links": {
            "conf": "https://doi.org/10.1007/s11063-021-10695-4"
        },
        "img": "/img/Publications/orvae_npl.png",
        "abstract": "Detecting human speech is foundational for a wide range of emerging intelligent applications. However, accurately detecting human speech is challenging, especially in the presence of unknown noise patterns. Generally, deep learning-based methods have shown to be more robust and accurate than statistical methods and other existing approaches. However, typically creating a noise-robust and more generalized deep learning-based Voice Activity Detection (VAD) system requires the collection of an enormous amount of annotated audio data. In this work, we develop a generalized model trained on limited types of human speeches with noisy backgrounds. Yet, it can detect human speech in the presence of various unseen noise types, which were not present in the training set. To achieve this, we propose a One-Class Residual connections-based Variational Autoencoder (ORVAE), which only requires a limited number of human speech data with noisy background for training, thereby eliminating the need for collecting data with diverse noise patterns. Evaluating ORVAE with three different datasets (synthesized TIMIT and NOI\nSEX-92, synthesized LibriSpeech and NOISEX-92, and a Publicly Recorded dataset), our method outperforms other one-class baseline methods, achieving 1-scores of over 90% for multiple Signal-to-Noise Ratio (SNR) levels."
    },
    {
        "title": "Evaluation of an Audio-Video Multimodal Deepfake Dataset using Unimodal and Multimodal Detectors",
        "authors": [
            "Hasam Khalid",
            "Minha Kim",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "ACM MM Workshop on Synthetic Multimedia - Audiovisual Deepfake Generation and Detection",
        "venue": "ADGD",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1145/3476099.3484315"
        },
        "img": "/img/Publications/ADGD21_hasam.png",
        "abstract": "Significant advancements made in the generation of deepfakes have caused security and privacy issues. Attackers can easily impersonate a person's identity in an image by replacing his face with the target person's face. Moreover, a new domain of cloning human voices using deep-learning technologies is also emerging. Now, an attacker can generate realistic cloned voices of humans using only a few seconds of audio of the target person. With the emerging threat of potential harm deepfakes can cause, researchers have proposed deepfake detection methods. However, they only focus on detecting a single modality, i.e., either video or audio. On the other hand, to develop a good deepfake detector that can cope with the recent advancements in deepfake generation, we need to have a detector that can detect deepfakes of multiple modalities, i.e., videos and audios. To build such a detector, we need a dataset that contains video and respective audio deepfakes. We were able to find a most recent deepfake dataset, Audio-Video Multimodal Deepfake Detection Dataset (FakeAVCeleb), that contains not only deepfake videos but synthesized fake audios as well. We used this multimodal deepfake dataset and performed detailed baseline experiments using state-of-the-art unimodal, ensemble-based, and multimodal detection methods to evaluate it. We conclude through detailed experimentation that unimodals, addressing only a single modality, video or audio, do not perform well compared to ensemble-based methods. Whereas purely multimodal-based baselines provide the worst performance."
    },
    {
        "title": "FakeAVCeleb: A Novel Audio-Video Multimodal Deepfake Dataset",
        "authors": [
            "Hasam Khalid",
            "Shahroz Tariq",
            "Minha Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Neural Information Processing Systems",
        "venue": "NeurIPS",
        "track": "Dataset Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2108.05080"
        },
        "img": "/img/Publications/fakeceleb_nips2021.png",
        "abstract": "While the significant advancements have made in the generation of deepfakes using deep learning technologies, its misuse is a well-known issue now. Deepfakes can cause severe security and privacy issues as they can be used to impersonate a person's identity in a video by replacing his/her face with another person's face. Recently, a new problem of generating synthesized human voice of a person is emerging, where AI-based deep learning models can synthesize any person's voice requiring just a few seconds of audio. With the emerging threat of impersonation attacks using deepfake audios and videos, a new generation of deepfake detectors is needed to focus on both video and audio collectively. To develop a competent deepfake detector, a large amount of high-quality data is typically required to capture real-world (or practical) scenarios. Existing deepfake datasets either contain deepfake videos or audios, which are racially biased as well. As a result, it is critical to develop a high-quality video and audio deepfake dataset that can be used to detect both audio and video deepfakes simultaneously. To fill this gap, we propose a novel Audio-Video Deepfake dataset, FakeAVCeleb, which contains not only deepfake videos but also respective synthesized lip-synced fake audios. We generate this dataset using the most popular deepfake generation methods. We selected real YouTube videos of celebrities with four ethnic backgrounds to develop a more realistic multimodal dataset that addresses racial bias, and further help develop multimodal deepfake detectors. We performed several experiments using state-of-the-art detection methods to evaluate our deepfake dataset and demonstrate the challenges and usefulness of our multimodal Audio-Video deepfake dataset."
    },
    {
        "title": "VFP290K: A Large-Scale Benchmark Dataset for Vision-based Fallen Person Detection",
        "authors": [
            "Jaeju An",
            "Jeong‐Ho Kim",
            "Hanbeen Lee",
            "Jinbeom Kim",
            "Junhyung Kang",
            "Minha Kim",
            "Saebyeol Shin",
            "Dong-Hee Hong",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Neural Information Processing Systems",
        "venue": "NeurIPS",
        "track": "Dataset Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2021,
        "links": {},
        "img": "/img/Publications/vfp290_nips.png",
        "abstract": "Detection of fallen persons due to, for example, health problems, violence, or accidents, is a critical challenge. Accordingly, detection of these anomalous events is of paramount importance for a number of applications, including but not limited to CCTV surveillance, security, and health care. Given that many detection systems rely on a comprehensive dataset comprising fallen person images collected under diverse environments and in various situations is crucial. However, existing datasets are limited to only specific environmental conditions and lack diversity. To address the above challenges and help researchers develop more robust detection systems, we create a novel, large-scale dataset for the detection of fallen persons composed of fallen person images collected in various real-world scenarios, with the support of the South Korean government. Our Vision-based Fallen Person (VFP290K) dataset consists of 294,714 frames of fallen persons extracted from 178 videos, including 131 scenes in 49 locations. We empirically demonstrate the effectiveness of the features through extensive experiments analyzing the performance shift based on object detection models. In addition, we evaluate our VFP290K dataset with properly divided versions of our dataset by measuring the performance of fallen person detecting systems. We ranked first in the first round of the anomalous behavior recognition track of AI Grand Challenge 2020, South Korea, using our VFP290K dataset, which can be found here. Our achievement implies the usefulness of our dataset for research on fallen person detection, which can further extend to other applications, such as intelligent CCTV or monitoring systems. The data and more up-to-date information have been provided at our VFP290K site."
    },
    {
        "title": "IVDR: Imitation learning with Variational inference and Distributional Reinforcement learning to find Optimal Driving Strategy",
        "authors": [
            "Kihyung Joo",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE International Conference on Machine Learning and Applications",
        "venue": "ICMLA",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1109/icmla52953.2021.00047"
        },
        "img": "/img/Publications/ivdr.png",
        "abstract": "Current state-of-the-art autonomous driving technology significantly advanced, leveraging reinforcement learning (RL) algorithms, because it is not easy to apply a rule-based driving method that reflects all the various traffic conditions. Indeed, reinforcement learning can produce the possible optimal driving strategy of urban, rural, and motorway roads in various environmental conditions such as speed limits and school zones. However, it is challenging to adjust the parameters of the reward mechanism in RL, because the driving style of each user is very different. And it takes a massive amount of time and resources to conduct RL by reflecting all complex traffic conditions. However, if RL imitates the driving behavior of an expert, RL algorithm can proceed more quickly. Therefore, we propose a novel imitation learning framework, which combines an expert's driving behavior with a continuous behavior of an agent. Further, a deep reinforcement learning approach is used to mimic the expert's driving behavior. Therefore, we propose imitation learning with variational inference and distributional reinforcement learning (IVDR) algorithm. Our results show that IVDR achieves 80% better learning speed than the learning speed of other approaches and outperforms 12% higher in average reward. Our work shows great promise of using RL for autonomous driving and real vehicle driving simulation."
    },
    {
        "title": "Efficient Multi-Scale Feature Generation Adaptive Network",
        "authors": [
            "Gwanghan Lee",
            "Minha Kim",
            "Minha Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1145/3459637.3482337"
        },
        "img": "/img/Publications/cikm22_gh.png",
        "abstract": "Recently, an early exit network, which dynamically adjusts the model complexity during inference time, has achieved remarkable performance. However, they were unsuccessful at resolving the performance drop of early classifiers that make predictions with insufficient high-level feature information. Consequently, the performance degradation of early classifiers had a devastating effect on the entire network performance sharing the backbone. In this paper, we propose an Efficient Multi-Scale Feature Generation Adaptive Network (EMGNet), which not only reduced the redundancy of the architecture but also generates multi-scale features to improve the performance of the early exit network."
    },
    {
        "title": "Crew Resource Management in Industry 4.0: Focusing on Human-Autonomy Teaming",
        "authors": [
            "Sunny Yun",
            "Simon Woo"
        ],
        "venue_full": "Korean Journal of Aerospace and Environmental Medicine",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.46246/kjasem.210013"
        },
        "img": null,
        "abstract": "In the era of the 4th industrial revolution, the aviation industry is also growing remarkably with the development of artificial intelligence and networks, so it is necessary to study a new concept of CRM, which is required in the process of operating state-of-the-art equipment. The automation system, which has been treated only as a tool, is changing its role as a decision-making agent with the development of AI, and it is necessary to set clear standards for the role and responsibility in the safety-critical field. We present a new perspective on the automation system in the CRM program through the understanding of the autonomous system. In the future, autonomous system will develop as an agent for human pilots to cooperate, and accordingly, changes in role division and reorganization of regulations are required."
    },
    {
        "title": "DLPNet: Dynamic Loss Parameter Network using Reinforcement Learning for Aerial Imagery Detection",
        "authors": [
            "Junhyung Kang",
            "Simon S Woo"
        ],
        "venue_full": "International Conference on Artificial Intelligence and Pattern Recognition",
        "venue": "AIPR",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1145/3488933.3489031"
        },
        "img": "/img/Publications/dlpnet_icpr21.png",
        "abstract": "We propose DLPNet, a novel RL module to enable robust and stable training while achieving high performance in practical small mini-batch size conditions. DLPNet observes input image patches and acts to select the optimal parameters of the dynamic focal loss function for the baseline detector with every mini-batch training iteration during the training phase."
    },
    {
        "title": "CoReD: Generalizing Fake Media Detection with Continual Representation using Distillation",
        "authors": [
            "Minha Kim",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Multimedia",
        "venue": "MM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1145/3474085.3475535"
        },
        "img": "/img/Publications/acmm21_minha.png",
        "abstract": "In this work, we apply continuous learning to neural networks' learning dynamics, emphasizing its potential to increase data efficiency significantly. We propose Continual Representation using Distillation (CoReD) method that employs the concept of Continual Learning (CoL), Representation Learning (ReL), and Knowledge Distillation (KD). We design CoReD to perform sequential domain adaptation tasks on new deepfake and GAN-generated synthetic face datasets, while effectively minimizing the catastrophic forgetting in a teacher-student model setting. Our extensive experimental results demonstrate that our method is efficient at domain adaptation to detect low-quality deepfakes videos and GAN-generated images from several datasets, outperforming the-state-of-art baseline methods."
    },
    {
        "title": "SmartConDetect: Highly Accurate Smart Contract CodeVulnerability Detection Mechanism using BERT",
        "authors": [
            "Sowon Jeon",
            "Gilhee Lee",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM KDD workshop on programming language processing",
        "venue": "PLP",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {},
        "img": "/img/Publications/smartcondetect.png",
        "abstract": "In this paper, we propose SmartConDetect to detect security vulnerabilities in smart contracts written in Solidity, which the most popular programming language for writing smart contracts on the Ethereum platform. SmartConDetect is designed as a static analysis tool to extract code fragments from smart contracts in Solidity and analyze code patterns using a pre-trained BERT model and a bidirectional LSTM model."
    },
    {
        "title": "Exploring the Asynchronous of the Frequency Spectra of GAN-generated Facial Images",
        "authors": [
            "Binh M. Le",
            "Simon S. Woo"
        ],
        "venue_full": "IJCAI Workshop on Safety and Security of Deep Learning",
        "venue": null,
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2112.08050"
        },
        "img": "/img/Publications/ijcai2021_overall_diag.png",
        "abstract": "The rapid progression of Generative Adversarial Networks (GANs) has raised a concern of their misuse for malicious purposes, especially in creating fake face images. Although many proposed methods succeed in detecting GAN-based synthetic images, they are still limited by the need for large quantities of the training fake image dataset and challenges for the detector's generalizability to unknown facial images. In this paper, we propose a new approach that explores the asynchronous frequency spectra of color channels, which is simple but effective for training both unsupervised and supervised learning models to distinguish GAN-based synthetic images. We further investigate the transferability of a training model that learns from our suggested features in one source domain and validates on another target domains with prior knowledge of the features' distribution. Our experimental results show that the discrepancy of spectra in the frequency domain is a practical artifact to effectively detect various types of GAN-based generated images."
    },
    {
        "title": "FReTAL: Generalizing Deepfake Detection using Knowledge Distillation and Representation Learning",
        "authors": [
            "Minha Kim",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on Media Forensics",
        "venue": "CVPRW",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1109/cvprw53098.2021.00111"
        },
        "img": "/img/Publications/fretalgd.png",
        "abstract": "As GAN-based video and image manipulation technologies become more sophisticated and easily accessible, there is an urgent need for effective deepfake detection technologies. Moreover, various deepfake generation techniques have emerged over the past few years."
    },
    {
        "title": "Neural network laundering: Removing black-box backdoor watermarks from deep neural networks",
        "authors": [
            "William Aiken",
            "Hyoungshick Kim",
            "Simon Woo",
            "Jungwoo Ryoo"
        ],
        "venue_full": "Computers & Security",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.58
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1016/j.cose.2021.102277"
        },
        "img": "/img/Publications/nb.jpg",
        "abstract": "Creating a state-of-the-art deep-learning system requires vast amounts of data, expertise, and hardware, yet research into embedding copyright protection for neural networks has been limited. One of the main methods for achieving such protection involves relying on the susceptibility of neural networks to backdoor attacks, but the robustness of these tactics has been primarily evaluated against pruning, fine-tuning, and model inversion attacks."
    },
    {
        "title": "Will EU’s GDPR Act as an Effective Enforcer to Gain Consent?",
        "authors": [
            "Junhyoung Oh",
            "Jinhyoung Hong",
            "Changsoo Lee",
            "Jemin Justin Lee",
            "Simon S. Woo",
            "Kyungho Lee"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.67
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1109/access.2021.3083897"
        },
        "img": "gdpr.PNG",
        "abstract": "In this study, we analyze GDPR provisions and recitals as well as relevant EU guidelines to propose quantifiable consent conditions to check whether website providers are compliant with the GDPR. We then evaluate the extent to which various popular web service providers meet these conditions."
    },
    {
        "title": "Am I a Real or Fake Celebrity? Measuring Commercial Face Recognition Web APIs under Deepfake Impersonation Attack",
        "authors": [
            "Shahroz Tariq",
            "Sowon Jeon",
            "Simon S. Woo"
        ],
        "venue_full": "arXiv",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2103.00847"
        },
        "img": "/img/Publications/airor.png",
        "abstract": "This work provides a measurement study on the robustness of black-box commercial face recognition APIs against Deepfake Impersonation (DI) attacks using celebrity recognition APIs as an example case study We achieved maximum success rates of 78.0% and 99.9% for targeted (ie, precise match) and non-targeted (ie, match with any celebrity) attacks, respectively. Moreover, we propose practical defense strategies to mitigate DI attacks, reducing the attack success rates to as low as 0% and 0.02% for targeted and non-targeted attacks, respectively."
    },
    {
        "title": "Revitalizing Self-Organizing Map: Anomaly Detection Using Forecasting Error Patterns",
        "authors": [
            "Young Geun Kim",
            "Jeong-Han Yun",
            "Siho Han",
            "Hyoung Chun Kim",
            "Simon S. Woo"
        ],
        "venue_full": "IFIP International Conference on ICT Systems Security and Privacy Protection",
        "venue": "IFIP SEC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-78120-0_25"
        },
        "img": "/img/Publications/rsom.png",
        "abstract": "In this work, we focus on improving the anomaly detection performance by leveraging the forecasting error patterns generated from prediction models, such as Sequence-to-Sequence (seq2seq), Mixture Density Networks (MDNs), and Recurrent Neural Networks (RNNs). To this end, we introduce Self-Organizing Map-based Anomaly Detector (SOMAD), an anomaly detection framework based on a novel test statistic, SomAnomaly, for Cyber-Physical System (CPS) security."
    },
    {
        "title": "TAR: Generalized Forensic Framework to Detect Deepfakes Using Weakly Supervised Learning",
        "authors": [
            "Sangyup Lee",
            "Shahroz Tariq",
            "Junyaup Kim",
            "Simon S. Woo"
        ],
        "venue_full": "IFIP International Conference on ICT Systems Security and Privacy Protection",
        "venue": "IFIP SEC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-78120-0_23"
        },
        "img": "/img/Publications/tgddw.png",
        "abstract": "This work introduces a practical digital forensic tool to detect different types of deepfakes simultaneously\n                                and proposes Transfer learning-based Autoencoder with Residuals (TAR). The ultimate goal\n                                of this work is to develop an uni fied model to detect various types of deepfake videos\n                                with high accuracy, with only a small number of training samples that can work well in\n                                real-world settings. To achieve this, this work develops an autoencoder-based detection\n                                model with Residual blocks and sequentially performs transfer learning to detect\n                                different types of deepfakes simultaneously. The detection model shows a high detection\n                                performance not only on the FF++ dataset but also on 200 real-world Deepfake-in-the-wild\n                                videos."
    },
    {
        "title": "Detecting handcrafted facial image manipulations and GAN-generated facial images using Shallow-FakeFaceNet",
        "authors": [
            "Sangyup Lee",
            "Shahroz Tariq",
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "Applied Soft Computing",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            5.47
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1016/j.asoc.2021.107256"
        },
        "img": "/img/Publications/dhfi.png",
        "abstract": "In this work, we introduce a novel Handcrafted Facial Manipulation (HFM) image dataset and soft computing neural network models (Shallow-FakeFaceNets) with an efficient facial manipulation detection pipeline. Our neural network classifier model, Shallow-FakeFaceNet (SFFN), shows the ability to focus on the manipulated facial landmarks to detect fake images. This study is targeted for developing an automated defense mechanism to combat fake images used in different online services and applications, leveraging our state-of-the-art handcrafted fake facial dataset (HFM) and the neural network classifier Shallow-FakeFaceNet (SFFN)."
    },
    {
        "title": "Exploring Racial Bias in Classifiers for Face Recognition",
        "authors": [
            "Jaeju An",
            "Jeongho Kim",
            "Bosung Yang",
            "Geonwoo Park",
            "Simon S. Woo"
        ],
        "venue_full": "WWW Workshop on Fairness, Accountability, Transparency, Ethics and Society on the Web",
        "venue": "FATES",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2021,
        "links": {},
        "img": "/img/Publications/ExploringRacialBias.png",
        "abstract": "Recent advancements in deep learning have allowed, among others,various applications of face recognition\n                                systems, where a largeamount of face image data are typically required for training."
    },
    {
        "title": "One Detector to Rule Them All: Towards a General Deepfake Attack Detection Framework",
        "authors": [
            "Shahroz Tariq",
            "Sang Yup Lee",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2021,
        "links": {},
        "img": "/img/Publications/odtr.png",
        "abstract": "Beyond detecting a single type of DF from benchmark deepfake datasets, we focus on developing a generalized approach to detect multiple types of DFs, including deepfakes from unknown generation methods such as DeepFake-in-the-Wild (DFW) videos. To better cope with unknown and unseen deepfakes, we introduce a Convolutional LSTM-based Residual Network (CLRNet), which adopts a unique model training strategy and explores spatial as well as the temporal information in a deepfakes. Through extensive experiments, we show that existing defense methods are not ready for real-world deployment. Whereas our defense method (CLRNet) achieves far better generalization when detecting various benchmark deepfake methods (97.57% on average). Furthermore, we evaluate our approach with a high-quality DeepFake-in-the-Wild dataset, collected from the Internet containing numerous videos and having more than 150,000 frames. Our CLRNet model demonstrated that it generalizes well against high-quality DFW videos by achieving 93.86% detection accuracy, outperforming existing state-of-the-art defense methods by a considerable margin."
    },
    {
        "title": "A Security Analysis of Blockchain-Based Did Services",
        "authors": [
            "Bong Gon Kim",
            "Young-Seob Cho",
            "Seok-Hyun Kim",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            4.09
        ],
        "year": 2021,
        "links": {
            "conf": "https://doi.org/10.1109/access.2021.3054887"
        },
        "img": "/img/Publications/secBlock.jpg",
        "abstract": "Decentralized identifiers (DID) has shown great potential for sharing user identities across different domains and services without compromising user privacy. DID is designed to enable the minimum disclosure of the proof from a user’s credentials on a need-to-know basis with a contextualized delegation."
    },
    {
        "title": "BertLoc: Duplicate Location Record Detection in a Large-Scale Location Dataset",
        "authors": [
            "Sujin Park",
            "Sangwon Lee",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2021,
        "links": {},
        "img": "/img/Publications/bertLoc.png",
        "abstract": "In this work, we propose BertLoc, a novel deep learning-based architecture to detect the duplicate location represented in different ways (e.g., Cafe vs. Coffee House) and effectively merge them into a single and consistent location record. BertLoc is based on Multilingual Bert Model followed by BiLSTM and CNN to effectively compare and determine whether given location strings are the same location or not. We evaluate BertLoc trained with more than half a million location data used in real service in South Korea and compare the results with other popular baseline methods. Our experimental results show that BertLoc outperforms other popular baseline methods with 0.952 F1-score, and shows great promise in detecting duplicate records in a large-scale location dataset."
    },
    {
        "title": "Image hashing algorithm to defend FGSM attacks on Neural Network",
        "authors": [
            "Junyaup Kim",
            "Siho Han",
            "Simon S. Woo"
        ],
        "venue_full": "Cyber Defence Next Generation Technology and Science Conference",
        "venue": "CDNG",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://dash-lab.github.io/img/Publications/jy.pdf"
        },
        "img": "/img/Publications/jy.png",
        "abstract": "In this research, we present a performance evaluation of existing image hashing algorithms on defending deep learning models against adversarial attacks as an initial work to developing a new, time efficient image hashing algorithm. Upon experimenting with existing image hashing algorithms, we conclude that the wavelet hashing algorithm achieves the highest accuracy (75%) when detecting images generated from Neural Networks attacked by the FGSM, with a time complexity of 𝑂(𝑁)."
    },
    {
        "title": "오픈소스 기반 격자 방식 PQC 알고리즘 분석 (Open-Source Code Analysis on Lattice-Based Post Quantum Cryptography)",
        "authors": [
            "Minha Kim",
            "Hakjun Moon",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Winter",
        "venue": "CISC-W",
        "track": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://dash-lab.github.io/img/Publications/pqc.pdf"
        },
        "img": "/img/Publications/pqc.png",
        "abstract": "Currently used cryptography algorithms like RSA are vulnerable to quantum computers and are at risk of being deciphered in polynomial time. As the commercialization of quantum computers is soon to be realized, there is an urgent need for developing post-quantum cryptography(PQC) algorithms. In this paper, we analyze several lattice-based PQC algorithms from NIST Post-Quantum Cryptography Standardization project and test them in some representative security protocols to show their practicality."
    },
    {
        "title": "Compensating for the Lack of Extra Training Data by Learning Extra Representation",
        "authors": [
            "Hyeonseong Jeon",
            "Siho Han",
            "Sangwon Lee",
            "Simon S. Woo"
        ],
        "venue_full": "Asian Conference on Computer Vision",
        "venue": "ACCV",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-69544-6_32"
        },
        "img": "/img/Publications/ctle.png",
        "abstract": "We introduce a novel framework, Extra Representation (ExRep), to surmount the problem of not having access to the JFT-300M data by instead using ImageNet and the publicly available model that has been pre-trained on JFT-300M. We take a knowledge distillation approach, treating the\n                                model pre-trained on JFT-300M as well as on ImageNet as the teacher network and that pre-trained only on ImageNet as the student network. Our proposed method is capable of learning additional representation effects of the teacher model, bolstering the student model’s performance to a similar level to that of the teacher model, achieving high classification performance even without extra training data."
    },
    {
        "title": "ITAD: Integrative Tensor-based Anomaly Detection System for Reducing False Postives of Satellite Systems",
        "authors": [
            "Youjin Shin",
            "Shahroz Tariq",
            "Sangyup Lee",
            "Myeong Shin Lee",
            "Okchul Jung",
            "Daewon Chung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2020,
        "links": {},
        "img": "/img/Publications/itad.png",
        "abstract": "Reducing false positives while detecting anomalies is of growing importance for various industrial applications and mission-critical infrastructures, including satellite systems. Undesired false positives can be costly for such systems, bringing the operation to a halt for human experts to determine if the anomalies are true anomalies that need to be mitigated"
    },
    {
        "title": "ZoomNet: Detecting Low-Quality Deepfakes In The Wild by Zooming In",
        "authors": [
            "Sangyup Lee",
            "Simon S. Woo",
            "Jinhwan Kim",
            "Okyeop Jeon"
        ],
        "venue_full": "Proceedings of the Korean Information Science Society Conference",
        "venue": "한국법과학회 2020 추계학술대회",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {},
        "img": "/img/Publications/zoomnet_2020.png",
        "abstract": "Deepfakes have become a critical social problem, and detecting them is of utmost importance. Detecting high-quality deepfake videos from widely released datasets is more straightforward to detect than low-quality ones. Most of the prior research achieve above 90% accuracy for detecting the high-quality deepfake videos from the open dataset. However, in real life, many deepfake videos that are leaked through social networks such as YouTube and instant messaging applications are highly compressed. As a result, the distributed video's resolution becomes extremely lower, making the state-of-the-art detection methods harder. In this work, we propose ZoomNet, a practical framework to detect low-quality deepfakes with high accuracy. We build ZoomNet to have the ability to zoom into low-quality images effectively and can learn to distinguish deepfakes from real videos."
    },
    {
        "title": "Who is Delivering My Food? Detecting Food Delivery Abusers using Variational Reward Inference Networks",
        "authors": [
            "DaeYoung Yoon",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2020,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1145/3340531.3412750"
        },
        "img": "/img/Publications/yoon.png",
        "abstract": "The recent paramount success of the gig economy has introduced new business opportunities in different areas such as food delivery service. However, there are food delivery ride abusers who break the company rule by driving unauthorized vehicles that are not stated in the contract"
    },
    {
        "title": "Can We Create a Cross-Domain Federated Identity for the Industrial Internet of Things without Google?",
        "authors": [
            "Eunsoo Kim",
            "Young-Seob Cho",
            "Bedeuro Kim",
            "Woojoong Ji",
            "Seok-Hyun Kim",
            "Simon S. Woo",
            "Hyoungshick Kim"
        ],
        "venue_full": "IEEE Internet of Things Magazine",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1109/iotm.0001.2000050"
        },
        "img": "/img/Publications/bc.png",
        "abstract": "Providing a cross-domain federated identity is essential for next-generation Internet services because information about user identity should be seamlessly exchanged across different domains for authentication and authorization."
    },
    {
        "title": "Applying Deep Learning to Reconstruct Pottery from Thousands Shards,",
        "authors": [
            "Keeyoung Kim",
            "Jinseok Hong",
            "Sang-Hoon Rhee",
            "Simon S. Woo"
        ],
        "venue_full": "European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases",
        "venue": "ECML-PKDD",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://link.springer.com/chapter/10.1007/978-3-030-67670-4_3"
        },
        "img": null,
        "abstract": "A great deal of time, patience, and effort are required to excavate pottery. For example, archaeologists dig hundreds to thousands of pottery shards from an excavation site. However, restoring pottery is a time-consuming and challenging process, requiring considerable amounts of expertise, experience, and time. "
    },
    {
        "title": "OC-FakeDect: Classifying Deepfakes Using One-class Variational Autoencoder",
        "authors": [
            "Hasam Khalid",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Biometrics Council newsletter",
        "venue": null,
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1109/cvprw50498.2020.00336"
        },
        "img": "/img/Publications/ocvae.png",
        "abstract": "An image forgery method called Deepfakes can cause security and privacy issues by changing the identity of a person in a photo through the replacement of his/her face with a computer-generated image or another person’s face."
    },
    {
        "title": "Forecasting Error Pattern-Based Anomaly Detection in Multivariate Time Series",
        "authors": [
            "Seoyoung Park",
            "Siho Han",
            "Simon S. Woo"
        ],
        "venue_full": "European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases",
        "venue": "ECML-PKDD",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-67667-4_10"
        },
        "img": "/img/Publications/fepb.jpg",
        "abstract": "We propose novel Functional Data Analysis (FDA) and Autoencoder-based approaches for anomaly detection in the Secure Water Treatment (SWaT) dataset, which realistically represents a scaled-down industrial water treatment plant. We demonstrate that our methods can capture the underlying forecasting error patterns of the SWaT dataset generated by Mixture Density Networks (MDNs)."
    },
    {
        "title": "국내 딥페이크 기술 현황 및 제도적 대응방안 연구",
        "authors": [
            "Sowon Jeon",
            "Junhyung Kang",
            "Jinhee Hwang",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Summer",
        "venue": "CISC-S",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {},
        "img": "/img/Publications/sowon1.png",
        "abstract": "최근 한국에서 ‘가짜 연예인 음란  동영상’ 및 ‘지인 능욕’에 사용되는 딥페이크(Deepfakes) 포르노 문제가 사회적인 이슈로 불거지고 있다. 딥페이크 기술은 인공지능 기술의 발전에 맞추어 더욱더 빠르게 발전하고 있으나 관련 규제와 대응방안이 부족한 실정이다. 따라서 본 논문에서는 딥페이크 기술의 현황과 딥페이크 관련 국내외 법적 규제 및 현행법의 한계점을 살펴보고, 이로부터 각 개인 및 기관의 역할과 대응방안을 제안한다."
    },
    {
        "title": "T-GD: Transferable GAN-generated Images Detection Framework",
        "authors": [
            "Hyeonseong Jeon",
            "Youngoh Bang",
            "Junyaup Kim",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Machine Learning",
        "venue": "ICML",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.48550/arxiv.2008.04115"
        },
        "img": "/img/Publications/tgd.png",
        "abstract": "In this work, we present the Transferable GAN-images Detection framework (T-GD), a robust transferable framework for an effective detection of GAN-images. T-GD is composed of a teacher and a student model that can iteratively teach and evaluate each other to improve the detection performance."
    },
    {
        "title": "Real Time Localized Air Quality Monitoring and Prediction Through Mobile and Fixed IoT Sensing Network",
        "authors": [
            "Dan Zhang",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            4.09
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1109/access.2020.2993547"
        },
        "img": null,
        "abstract": "Air pollution and its harm to human health has become a serious problem in many cities around the world.In recent years, research interests in measuring and predicting the quality of air around people has spiked."
    },
    {
        "title": "CAN-ADF: The controller area network attack detection framework",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Huy Kang Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Computers & Security",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.58
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1016/j.cose.2020.101857"
        },
        "img": "/img/Publications/canadf.png",
        "abstract": "In recent years, there has been significant interest in developing autonomous vehicles such as self-driving cars. In-vehicle communications, due to simplicity and reliability, a Controller Area Network (CAN) bus is widely used as the de facto standard to provide serial communications between Electronic Control Units (ECUs)"
    },
    {
        "title": "OC-FakeDect: Classifying Deepfakes Using One-class Variational Autoencoder",
        "authors": [
            "Hasam Khalid",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on Media Forensics",
        "venue": "CVPRW",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://openaccess.thecvf.com/content_CVPRW_2020/papers/w39/Khalid_OC-FakeDect_Classifying_Deepfakes_Using_One-Class_Variational_Autoencoder_CVPRW_2020_paper.pdf"
        },
        "img": "/img/Publications/ocvae.png",
        "abstract": "In recent years, there has been significant interest in developing autonomous vehicles such as self-driving cars. In-vehicle communications, due to simplicity and reliability, a Controller Area Network (CAN) bus is widely used as the de facto standard to provide serial communications between Electronic Control Units (ECUs)"
    },
    {
        "title": "Design and Evaluation of Enumeration Attacks on Package Tracking Systems",
        "authors": [
            "Hanbin Jang",
            "Woojoong Ji",
            "Simon S. Woo",
            "Hyoungshick Kim"
        ],
        "venue_full": "Australasian Conference on Information Security and Privacy",
        "venue": "ACISP",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-55304-3_28"
        },
        "img": null,
        "abstract": "Most shipping companies provide a package tracking system where customers can easily track their package delivery status when the package is being shipped. However, we present asecurity problem called enumeration attacks against package tracking systems..."
    },
    {
        "title": "How Do We Create a Fantabulous Password?",
        "authors": [
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1145/3366423.3380222"
        },
        "img": null,
        "abstract": "Although pronounceability can improve password memorability, most existing password generation approaches have not properly integrated the pronounceability of passwords in their designs. In this work, we demonstrate several shortfalls of current pronounceable password generation\n                            approaches, and then propose, ProSemPass, a new method of generating passwords that are pronounceable and semantically meaningful."
    },
    {
        "title": "I’ve Got Your Packages: Harvesting Customers’ Delivery Order Information using Package Tracking Number Enumeration Attacks",
        "authors": [
            "Simon Woo",
            "Hanbin Jang",
            "Woojung Ji",
            "Hyoungshick Kim"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1145/3366423.3380062"
        },
        "img": null,
        "abstract": "A package tracking number (PTN) is widely used to monitor and track a shipment. Through the lenses of security and privacy, however, a package tracking number can possibly reveal certain personal information, leading to security and privacy breaches."
    },
    {
        "title": "FDFtNet: Facing Off Fake Images Using Fake Detection Fine-Tuning Network",
        "authors": [
            "Hyeonseong Jeon",
            "Youngoh Bang",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Information Security and Privacy Protection",
        "venue": "IFIP SEC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-58201-2_28"
        },
        "img": null,
        "abstract": "Creating fake images and videos such as Deepfake has become much easier these days due to the advancement in Generative Adversarial Networks (GANs). Moreover, recent research such as the few-shot learning can create highly realistic personalized fake images with only a few images."
    },
    {
        "title": "PassTag: A Graphical-Textual Hybrid Fallback Authentication System",
        "authors": [
            "Joon Kuy Han",
            "Xiaojun Bi",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Asia Conference on Computer and Communications Security,",
        "venue": "ASIACCS",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1145/3320269.3384737"
        },
        "img": null,
        "abstract": "Designing a fallback authentication mechanism that is both memorable and strong is a challenging problem because of the trade-off between usability and security. Security questions are popularly used as a fallback authentication method for password recovery."
    },
    {
        "title": "Tale of Two Browsers: Understanding Users’ Web Browser Choices in South Korea",
        "authors": [
            "Jihye Woo",
            "Ji Won Choi",
            "Soyoon Jeon",
            "Joon Kuy Han",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Asian Workshop on Usable Security",
        "venue": "AsiaUSEC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2020,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-54455-3_1"
        },
        "img": null,
        "abstract": "Internet users in South Korea seem to have clearly different web browser choices and usage patterns compared to the rest of the world, heavily using Internet Explorer (IE) or multiple browsers."
    },
    {
        "title": "CANTransfer: Transfer Learning based Intrusion Detection on a Controller Area Network using Convolutional LSTM Network",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium On Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2020,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1145/3341105.3373868"
        },
        "img": "/img/Publications/cantransfer.png",
        "abstract": "In-vehiclecommunications, due to simplicity and reliability, a Controller Area Network (CAN) bus is widely used as the de facto standard to provide serial communications between Electronic Control Units (ECUs)."
    },
    {
        "title": "Designing for Fallible Humans",
        "authors": [
            "Jelena Mirkovic",
            "Simon Woo"
        ],
        "venue_full": "International Conference on Collaboration and Internet Computing",
        "venue": "CIC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1109/cic48465.2019.00042"
        },
        "img": null,
        "abstract": "Security and privacy solutions today are designed with an assumption of a rational user. System designers assume that the user is able to review all information shown to them, consider it along with other information they have, and user priorities, and make a conscious, rational decision in their best interest."
    },
    {
        "title": "Poster: Classifying Genuine Face images from Disguised Face Images",
        "authors": [
            "Junyaup Kim",
            "Siho Han",
            "Simon S.Woo"
        ],
        "venue_full": "IEEE International Conference on Big Data",
        "venue": "IEEE BigData",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://ieeexplore.ieee.org/abstract/document/9005683"
        },
        "img": "/img/Publications/cgfi.png",
        "abstract": "In this preliminary work, we aim to detect a target person's face from different similar individuals, Doppelgangers, leveraging the dataset from Disguised Faces in the Wild (DFW) 2018. We use well-known off-the-shelf face detection classifiers, such as ShallowNet, VGG-16, and Xception to evaluate the classification performance. In order to further improve the detection performance, we apply data augmentation. Our preliminary result shows that the Xception model can classify one from different individuals with a 62% accuracy."
    },
    {
        "title": "Poster: Nickel to Lego: Using Foolgle to Create Adversarial Examples to fool Google Cloud Speech-to-Text API,",
        "authors": [
            "Joon Kuy Han",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Conference on Computer and Communications Security",
        "venue": "CCS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1145/3319535.3363264"
        },
        "img": null,
        "abstract": "Many companies offer automatic speech recognition or Speech-to-Text APIs for use in diverse applications. However, audio classification algorithms trained with deep neural networks (DNNs) can sometimes misclassify adversarial examples, posing a significant threat to critical applications."
    },
    {
        "title": "Deep Learning for Blast Furnaces: Skip-Dense Layers Deep Learning Model to Predict the emaining Time to Close Tap-holes for Blast Furnaces",
        "authors": [
            "Keeyoung Kim",
            "Byeongrak Seo",
            "Sang-Hoon Rhee",
            "Seungmoon Lee",
            "Simon S. Woo"
        ],
        "venue_full": "ACM International Conference on Information and Knowledge Management",
        "venue": "CIKM",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2019,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1145/3357384.3357803"
        },
        "img": null,
        "abstract": "Manufacturing steel requires extremely challenging industrial processes. In particular, predicting the exact time instance of opening and closing tap-holes in a blast furnace has a great influence on steel production efficiency and operating cost, in addition to human safety."
    },
    {
        "title": "FakeTalkerDetect: Effective and Practical Realistic Neural Talking Head Detection with a Highly Unbalanced Dataset",
        "authors": [
            "Hyeonseong Jeon",
            "Youngoh Bang",
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF ICCV Workshop on Human Behavior Understanding",
        "venue": "HBU",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1109/iccvw.2019.00163"
        },
        "img": null,
        "abstract": "Detecting realistic fake images and videos is an increasingly important and urgent problem because they can be maliciously used. In this work, we propose FakeTalkerDetect, which is based on siamese networks to detect the recently proposed realistic talking head with few-shot learning."
    },
    {
        "title": "Tensor Decomposition for Anomaly Detection in Space",
        "authors": [
            "Youjin Shin",
            "Sangyup Lee",
            "Shahroz Tariq",
            "Simon S. Woo"
        ],
        "venue_full": "ACM KDD Workshop on Tensor Methods for Emerging Data Science Challenges",
        "venue": "TMEDSC",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://milets19.github.io/papers/milets19_poster_6.pdf"
        },
        "img": "/img/Publications/tdfad.png",
        "abstract": ""
    },
    {
        "title": "Contextual Anomaly Detection by Correlated Probability Distributions using Kullback-Leibler Divergence",
        "authors": [
            "Jinwoo Cho",
            "Shahroz Tariq",
            "Sangyup Lee",
            "Young Geun Kim",
            "Jeong-Han Yun",
            "Jonguk Kim",
            "Hyoung Chun Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM KDD Workshop on Mining and Learning from Time Series",
        "venue": null,
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2019,
        "links": {
            "conf": "https://ygeunkim.github.io/publication/kl_poster/"
        },
        "img": "/img/Publications/cad.png",
        "abstract": ""
    },
    {
        "title": "Detecting Anomalies in Space using Multivariate Convolutional LSTM with Mixtures of Probabilistic PCA",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Youjin Shin",
            "Myeong Shin Lee",
            "Okchul Jung",
            "Daewon Chung",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "venue": "KDD",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1145/3292500.3330776"
        },
        "img": "/img/Publications/dais.png",
        "abstract": "Detecting an anomaly is not only important for many terrestrial applications on Earth but also for space applications. Especially, satellite missions are highly risky because unexpected hardware and software failures can occur due to sudden or unforeseen space environment changes."
    },
    {
        "title": "Understanding Users' Risk Perceptions about Personal Health Records Shared on Social Networking Services",
        "authors": [
            "Yuri Son",
            "Geumhwan Cho",
            "Hyoungshick Kim",
            "Simon Woo"
        ],
        "venue_full": "ACM Asia Conference on Computer and Communications Security,",
        "venue": "ASIACCS",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1145/3321705.3329838"
        },
        "img": null,
        "abstract": "To understand users' risk perceptions about sharing their PHR on SNS, we first conducted a qualitative user study by interviewing 16 participants. Next, we conducted a large-scale online user study with 497 participants in the U.S. to validate our qualitative results from the first study."
    },
    {
        "title": "You Walk, We Authenticate: Lightweight Seamless Authentication Based on Gait in Wearable IoT Systems",
        "authors": [
            "Pratik Musale",
            "Duin Baek",
            "Nuwan Werellagama",
            "Simon S. Woo",
            "Bong Jun Choi"
        ],
        "venue_full": "IEEE Access",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.557
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1109/access.2019.2906663"
        },
        "img": null,
        "abstract": "With a plethora of wearable IoT devices available today, we can easily monitor human activities, many of which are unconscious or subconscious. Interestingly, some of these activities exhibit distinct patterns for each individual, which can provide an opportunity to extract useful features for user authentication."
    },
    {
        "title": "What is in Your Password? Analyzing Memorable and Secure Passwords using a Tensor Decomposition",
        "authors": [
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            3
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1145/3308558.3313690"
        },
        "img": null,
        "abstract": "In the past, there have been several studies in analyzing password strength and structures. However, there are still many unknown questions to understand what really makes passwords both memorable and strong. In this work, we aim to answer some of these questions by analyzing password dataset through the lenses of data science and machine learning perspectives."
    },
    {
        "title": "Using Episodic Memory for User Authentication",
        "authors": [
            "Simon S. Woo",
            "Ron Artstein",
            "Elsi Kaiser",
            "Xiao Le",
            "Jelena Mirkovic"
        ],
        "venue_full": "ACM Transactions on Transactions on Privacy and Security ",
        "venue": "TOPS",
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            2.1
        ],
        "year": 2019,
        "links": {
            "conf": "https://doi.org/10.1145/3308992"
        },
        "img": null,
        "abstract": "Passwords are widely  used for user authentication, but they are often difficult for a user to recall, easily cracked by automated programs, and heavily reused. Security questions are also used for secondary authentication. They are more memorable than passwords, because the question serves as a hint to the user, but they are very easily guessed. We propose a new authentication mechanism, called life-experience passwords (LEPs)."
    },
    {
        "title": "GAN is a Friend or Foe? A Framework to Detect Various Fake Face Images",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Youjin Shin",
            "Ho Young Kim",
            "Simon S. Woo"
        ],
        "venue_full": "ACM SIGAPP Symposium on Applied Computing",
        "venue": "SAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2019,
        "links": {},
        "img": "/img/Publications/ganfof.png",
        "abstract": "Creating fake images such as replacing one's face with other person's face has become much easier due to the advancement of sophisticated image editing tools. In addition, Generative Adversarial Networks (GANs) enable creating natural looking human faces. However, fake images can cause many potential problems, as they can be misused to abuse information, hurt people, and generate fake identification."
    },
    {
        "title": "Design and evaluation of 3D CAPTCHAs",
        "authors": [
            "Simon S. Woo"
        ],
        "venue_full": "Computers & Security,",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            3.06
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1016/j.cose.2018.12.006"
        },
        "img": null,
        "abstract": "Most current 2D CAPTCHAs are vulnerable to automated character recognition attacks and the latest attacks can successfully break the 2D text CAPTCHAs at a rate of more than 90%. In this work, we present two novel 3D CAPTCHAs, which are more secure than current 2D text CAPTCHAs against automated character recognition attacks."
    },
    {
        "title": "Poster: Memorability and Security of Image and Text Integrated Authentication System",
        "authors": [
            "Joonkyu Han and Simon S. Woo"
        ],
        "venue_full": "Annual Computer Security Applications Conference",
        "venue": "ACSAC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Evaluating and Breaking Naver’s Audio CAPTCHA using Off-the-Shelf Speech-to-text APIs",
        "authors": [
            "Soyoon Jeon",
            "Jihye Woo",
            "Ji Won Choi",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Winter",
        "venue": "CISC-W",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Understanding Users’ Perception on Digital Certificate and Their Web Browser Usages in Korea",
        "authors": [
            "Jihye Woo",
            "Soyoon Jeon",
            "Ji Won Choi",
            "Hyoungshick Kim",
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Winter",
        "venue": "CISC-W",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1007/978-3-030-54455-3_1"
        },
        "img": null,
        "abstract": ""
    },
    {
        "title": "Password typographical error resilience in honey encryption",
        "authors": [
            "Hoyul Choi",
            "Jongmin Jeong",
            "Simon S. Woo",
            "Kyungtae Kang",
            "Junbeom Hur"
        ],
        "venue_full": "Computers & Security",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            2.86
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1016/j.cose.2018.07.020"
        },
        "img": null,
        "abstract": "Honey encryption (HE) is a novel password-based encryption scheme that is secure against brute-force attacks even if users’ passwords have min-entropy. However, in HE, decryption with an incorrect key produces fake messages that appear valid. Hence, password typographical errors may confuse even legitimate users."
    },
    {
        "title": "Poster: Adversarial Product Review Generation with Word Replacements",
        "authors": [
            "Yimin Zhu",
            "Simon S. Woo"
        ],
        "venue_full": "ACM Conference on Computer and Communications Security ",
        "venue": "CCS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1145/3243734.3278492"
        },
        "img": "/img/Publications/aprg.png",
        "abstract": "Machine learning algorithms including Deep Neural Networks (DNNs) have shown great success in many different areas. However, they are frequently susceptible to adversarial examples, which are maliciously crafted inputs to fool machine learning classifiers. On the other hand, humans cannot distinguish between non-adversarial and adversarial inputs."
    },
    {
        "title": "Detecting In-vehicle CAN Message Attacks Using Heuristics and RNNs",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Huy Kang Kim",
            "Simon S. Woo"
        ],
        "venue_full": "International workshop on Information & Operational Technology ",
        "venue": "IT & OT",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-030-12085-6_4"
        },
        "img": "/img/Publications/dican.png",
        "abstract": "In vehicle communications, due to simplicity and reliability, a Controller Area Network (CAN) bus is used as the de facto standard to provide serial communication between Electronic Control Units (ECUs). However, prior research reveals that several network-level attacks can be performed on the CAN bus due to the lack of underlying security mechanism."
    },
    {
        "title": "Detecting Both Machine and Human Created Fake Face Images In the Wild",
        "authors": [
            "Shahroz Tariq",
            "Sangyup Lee",
            "Hoyoung Kim",
            "Youjin Shin",
            "Simon S. Woo"
        ],
        "venue_full": "CCS Workshop on Multimedia Privacy and Security",
        "venue": "MPS",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1145/3267357.3267367"
        },
        "img": "/img/Publications/dbmh.png",
        "abstract": "Due to the significant advancements in image processing and machine learning algorithms, it is much easier to create, edit, and produce high quality images. However, attackers can maliciously use these tools to create legitimate looking but fake images to harm others, bypass image detection algorithms, or fool image recognition classifiers."
    },
    {
        "title": "GuidedPass: Guiding users to create both more memorable and strong passwords",
        "authors": [
            "Simon S. Woo",
            "and Jelena Mirkovic"
        ],
        "venue_full": "International Symposium on Research in Attacks, Intrusions and Defenses",
        "venue": "RAID",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2018,
        "links": {
            "conf": "https://www.researchgate.net/publication/327469039_GuidedPass_Helping_Users_to_Create_Strong_and_Memorable_Passwords_21st_International_Symposium_RAID_2018_Heraklion_Crete_Greece_September_10-12_2018_Proceedings"
        },
        "img": null,
        "abstract": "Password meters and policies are currently the only tools helping users to create stronger passwords. However, such tools often do not provide consistent or useful feedback to users, and their suggestions may decrease memorability of resulting passwords."
    },
    {
        "title": "Poster: Leveraging Semantic Transformation to Investigate Password Habits and Their Causes",
        "authors": [
            "Ameya Hanamsagar",
            "Simon S. Woo",
            "Chris Kanich",
            "Jelena Mirkovic"
        ],
        "venue_full": "Usenix Symposium on Usable Privacy and Security",
        "venue": "SOUPS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1145/3173574.3174144"
        },
        "img": null,
        "abstract": "It is no secret that users have difficulty choosing and remembering strong passwords, especially when asked to choose different passwords across different accounts. While research has shed light on password weaknesses and reuse, less is known about user motivations for following bad password practices."
    },
    {
        "title": "When George Clooney Is Not George Clooney: Using GenAttack to Deceive Amazon’s and Naver’s Celebrity Recognition APIs",
        "authors": [
            "Keeyoung Kim",
            "Simon S. Woo"
        ],
        "venue_full": "International Conference on Information Security and Privacy Protection",
        "venue": "IFIP SEC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            1
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-319-99828-2_25"
        },
        "img": null,
        "abstract": "In recent years, significant advancements have been made in detecting and recognizing contents of images using Deep Neural Networks (DNNs). As a result, many companies offer image recognition APIs for use in diverse applications. However, image classification algorithms trained with DNNs can misclassify adversarial examples, posing a significant threat to critical applications."
    },
    {
        "title": "Generating Adversarial Images using Genetic Algorithm",
        "authors": [
            "Keeyoung Kim and Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on The Bright and Dark Sides of Computer Vision: Challenges and Opportunities for Privacy and Security",
        "venue": "CV-COPS",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://www.researchgate.net/publication/339840424_Generating_Adversarial_Images_using_Genetic_Algorithm"
        },
        "img": null,
        "abstract": ""
    },
    {
        "title": "Poster: I can’t hear this because I am human: A novel design of audio CAPTCHA system",
        "authors": [
            "Jusop Choi",
            "Taekkyung Oh",
            "William Aiken",
            "Simon S. Woo",
            "Hyoungshick Kim"
        ],
        "venue_full": "ACM Asia Conference on Computer and Communications Security",
        "venue": "ASIACCS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://dl.acm.org/doi/10.1145/3196494.3201590"
        },
        "img": null,
        "abstract": "A CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) provides the first line of defense to protect websites against bots and automatic crawling. Recently, audio-based CAPTCHA systems are started to use for visually impaired people in many internet services."
    },
    {
        "title": "Benefits and Challenges of Long Term Self-Tracking to Prevent Lonely Deaths and Detect Signs of Life",
        "authors": [
            "Simon S. Woo"
        ],
        "venue_full": "Conference on Human Factors in Computing Systems",
        "venue": "CHI",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {},
        "img": null,
        "abstract": "We explore the benefit of a new long-term self-tracking application for the elderly population. In the last few years, there has been a significant increase in number of people dying alone or remaining undiscovered for a long period time in Korea and Japan."
    },
    {
        "title": "Leveraging Semantic Transformation to Investigate Password Habits and Their Causes",
        "authors": [
            "Ameya Hanamsagar",
            "Simon S. Woo",
            "Chris Kanich",
            "Jelena Mirkovic"
        ],
        "venue_full": "Conference on Human Factors in Computing Systems",
        "venue": "CHI",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            4
        ],
        "year": 2018,
        "links": {
            "conf": "https://doi.org/10.1145/3173574.3174144"
        },
        "img": null,
        "abstract": "It is no secret that users have difficulty choosing and remembering strong passwords, especially when asked to choose different passwords across different accounts. While research has shed light on password weaknesses and reuse, less is known about user motivations for following bad password practices."
    },
    {
        "title": "Memorablity and Security of Different Passphrase Generation Methods",
        "authors": [
            "Simon S. Woo",
            "Jelena Mirković"
        ],
        "venue_full": "Korea Institute of Information Security and Cryptology",
        "venue": "KIISC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE07399563"
        },
        "img": null,
        "abstract": "Passphrases are considered to be more secure than passwords since they are longer than passwords. However, users choose predictable word patterns and common phrases to make passphrases memorable, which in turn significantly lowers security. While random passphrases appear to be stronger, surprisingly they are neither strong nor memorable. In this paper, we present the latest passphrase research, and introduce a new way to create a passphrase using mnemonics. Passphrase generation using mnemonics shows promising results in improving both strength and memorability."
    },
    {
        "title": "Survey on Current Password Composition Policies",
        "authors": [
            "Simon S. Woo",
            "Kyeong Joo Jung",
            "Bong Jun Choi"
        ],
        "venue_full": "Korea Institute of Information Security and Cryptology",
        "venue": "KIISC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2018,
        "links": {
            "conf": "https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE07399565"
        },
        "img": null,
        "abstract": "Textual passwords are widely used for accessing online accounts. Despite the problems of current textual passwords, research has shown that there is no other strong alternatives for a textual password due to its simplicity."
    },
    {
        "title": "Lightweight Authentication for IoT",
        "authors": [
            "Pratik Musale",
            "Duin Baek",
            "Simon S. Woo",
            "Bong Jun Choi"
        ],
        "venue_full": "ACM Conference on Emerging Networking Experiments and Technologies",
        "venue": "CoNEXT",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2017,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Toward Machine Generated Passwords",
        "authors": [
            "Simon S. Woo",
            "Wenzhi Li",
            "Hyeran Jeon"
        ],
        "venue_full": "Conference on Information Security and Cryptography-Winter",
        "venue": "CISC-W",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2017,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Computer Vision Attacks against 3D CAPTCHAs",
        "authors": [
            "Simon S. Woo"
        ],
        "venue_full": "IEEE/CVF CVPR Workshop on The Bright and Dark Sides of Computer Vision: Challenges and Opportunities for Privacy and Security",
        "venue": "CV-COPS",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2017,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Life-experience passwords (LEPs)",
        "authors": [
            "Simon Woo",
            "Elsi Kaiser",
            "Ron Artstein",
            "Jelena Mirkovic"
        ],
        "venue_full": "Usenix Symposium on Usable Privacy and Security",
        "venue": "SOUPS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2017,
        "links": {
            "conf": "https://doi.org/10.1145/2991079.2991107"
        },
        "img": null,
        "abstract": null
    },
    {
        "title": "Improving Recall and Security of Passphrases Through Use of Mnemonics",
        "authors": [
            "Simon S. Woo",
            "Jelena Mirkovic"
        ],
        "venue_full": "International Conference on Passwords ",
        "venue": "Password",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2016,
        "links": {},
        "img": null,
        "abstract": "Passphrases are regarded as more secure than passwords because they are longer than passwords. Yet, users use predictable word patterns and common phrases to make passphrases memorable, which in turn significantly lowers security."
    },
    {
        "title": "Life-experience passwords (LEPs)",
        "authors": [
            "Simon Woo",
            "Elsi Kaiser",
            "Ron Artstein",
            "Jelena Mirkovic"
        ],
        "venue_full": "Annual Conference on Computer Security Applications",
        "venue": "ACSAC",
        "track": "Main Paper",
        "presentationType": null,
        "Factor": [
            "BK Computer Science IF=",
            2
        ],
        "year": 2016,
        "links": {
            "conf": "https://doi.org/10.1145/2991079.2991107"
        },
        "img": null,
        "abstract": "Passwords are widely used for user authentication, but they are often difficult for a user to recall, easily cracked by automated programs and heavily reused. Security questions are also used for secondary authentication. They are more memorable than passwords, but are very easily guessed. We propose a new authentication mechanism, called life-experience passwords (LEPs), which outperforms passwords and security questions, both at recall and at security."
    },
    {
        "title": "Good Automatic Authentication Question Generation",
        "authors": [
            "Simon Woo",
            "Zuyao Li",
            "Jelena Mirkovic"
        ],
        "venue_full": "International Natural Language Generation conference",
        "venue": "INLG",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2016,
        "links": {
            "conf": "https://doi.org/10.18653/v1/w16-6632"
        },
        "img": null,
        "abstract": "We explore a novel application of Question Generation (QG) for authentication use, where questions are widely used to verify user identity for online accounts. In our approach, we prompt users to provide a few sentences about their personal life events."
    },
    {
        "title": "Exploration of 3D Texture and Projection for New CAPTCHA Design",
        "authors": [
            "Simon S. Woo",
            "Jingul Kim",
            "Duoduo Yu",
            "Beomjun Kim"
        ],
        "venue_full": "World Conference on Information Security Applications",
        "venue": "WISA",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2016,
        "links": {
            "conf": "https://doi.org/10.1007/978-3-319-56549-1_30"
        },
        "img": null,
        "abstract": "Most of current text-based CAPTCHAs have been shown to be easily breakable. In this work, we present two novel 3D CAPTCHA designs, which are more secure than current 2D text CAPTCHAs, against automated attacks. Our approach is to display CAPTCHA characters onto 3D objects to improve security."
    },
    {
        "title": "Empirical Data Analysis on User Privacy and Sentiment in Personal Blogs",
        "authors": [
            "Simon S. Woo",
            "Harsha Manjunatha"
        ],
        "venue_full": " ACM SIGIR Workshop on Privacy-Preserving Information Retrieval",
        "venue": "PPIR",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2015,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Engaging Novices in Cybersecurity Competitions: A Vision and Lessons Learned at ACM Tapia 1025",
        "authors": [
            "Jelena Mirković",
            "Aimee Tabor",
            "Simon S. Woo",
            "Portia Pusey"
        ],
        "venue_full": "USENIX Summit on Gaming, Games, and Gamification in Security Education",
        "venue": "3GSE",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2015,
        "links": {
            "conf": "https://steel.isi.edu/members/simonwoo/pub/pir.pdf"
        },
        "img": null,
        "abstract": "Cybersecurity competitions are popular tools for attracting students to cybersecurity field. Yet, many competitions require extensive preparation, strong coding skills and solid background knowledge, not just in security, but also in system administration, networking and operating systems. As such, competitions may discourage novices that lack in one of these required areas. In this paper we discuss our experience in using Class Capture-theFlag Exercises (CCTFs) to bridge this gap in classes, and in 2015 ACM Richard Tapia Security workshop. We recount lessons learned and map a way forward, towards collaborative, more structured cybersecurity competitions that better support and engage novices, and offer a positive learning experience to all."
    },
    {
        "title": "Optimal application allocation on multiple public clouds",
        "authors": [
            "Simon S. Woo",
            "Jelena Mirkovic"
        ],
        "venue_full": "Computer Networks,",
        "venue": null,
        "track": "SCIE Journal",
        "presentationType": null,
        "Factor": [
            "SCIE IF =",
            2.52
        ],
        "year": 2014,
        "links": {
            "conf": "https://doi.org/10.1016/j.comnet.2013.12.001"
        },
        "img": null,
        "abstract": "Cloud computing customers currently host all of their application components at a single cloud provider. Single-provider hosting eases maintenance tasks, but reduces resilience to failures. Recent research (Li et al., 2010) also shows that providers offers differ greatly in erformance and price, and no single provider is the best in all service categories."
    },
    {
        "title": "Life-Experice Passwords",
        "authors": [
            "Simon S. Woo",
            "Jelena Mikovic",
            "Ron Artstein",
            "Elsi Kaiser"
        ],
        "venue_full": "Who are you?! Adventures in Authentication: ACM SOUPS-WAY Workshop",
        "venue": "WAY",
        "track": "Workshop Paper",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2014,
        "links": {},
        "img": null,
        "abstract": "Passwords are widely used for user authentication, but they are often difficult for a user to recall, easily cracked by automated programs and heavily reused. Security questions are also used for secondary authentication. They are more memorable than passwords, but are very easily guessed. We propose a new authentication mechanism, called life-experience passwords (LEPs), which outperforms passwords and security questions, both at recall and at security."
    },
    {
        "title": "Poster: 3DOC: 3D Object CAPTCHA",
        "authors": [
            "Simon S. Woo",
            "B. Kim"
        ],
        "venue_full": "Information Sciences Institute Graduate Student Symposium ",
        "venue": "ISI-GSS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2014,
        "links": {},
        "img": null,
        "abstract": "Current 2D CAPTCHA mechanisms can be easily defeated by character recognition and segmentation attacks by automated machines. Recently, 3D CAPTCHA schemes have been proposed to overcome the weaknesses of 2D CAPTCHA for a few websites."
    },
    {
        "title": "3DOC: 3D Object CAPTCHA",
        "authors": [
            "Simon S. Woo",
            "B. Kim"
        ],
        "venue_full": "ACM Web Conference",
        "venue": "WWW",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2014,
        "links": {},
        "img": null,
        "abstract": "Current 2D CAPTCHA mechanisms can be easily defeated by character recognition and segmentation attacks by automated machines. Recently, 3D CAPTCHA schemes have been proposed to overcome the weaknesses of 2D CAPTCHA for a few websites."
    },
    {
        "title": "Life Experience-Passwords",
        "authors": [
            "Simon S. Woo",
            "Jelena Mirkovic",
            "Elsi Kaiser"
        ],
        "venue_full": "Network and Distributed System Security",
        "venue": "NDSS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2014,
        "links": {},
        "img": null,
        "abstract": ""
    },
    {
        "title": "Analysis of Proximity-1 Space Link Interleaved Time Synchronization Protocol",
        "authors": [
            "Simon. S. Woo"
        ],
        "venue_full": "IEEE Global Telecommunications Conference",
        "venue": "GLOBECOM",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2011,
        "links": {
            "conf": "https://doi.org/10.1109/glocom.2011.6134144"
        },
        "img": null,
        "abstract": "To synchronize clocks between spacecraft in proximity, the Proximity-1 Space Link Interleaved Time Synchronization (PITS) Protocol has been proposed. PITS is based on the NTP Interleaved On-Wire Protocol and is capable of being adapted and integrated into CCSDS Proximity-1 Space Link with minimal modifications."
    },
    {
        "title": "MACHETE: A Protocol Evaluation Tool for Space-Based Networking Architecture and Simulation",
        "authors": [
            "Esther Jennings",
            "John Segui",
            "Simon S. Woo"
        ],
        "venue_full": "AIAA International Conference on Space Operations",
        "venue": "SpaceOps",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2010,
        "links": {
            "conf": "https://doi.org/10.2514/6.2010-2260"
        },
        "img": null,
        "abstract": "Space Exploration missions requires the design and implementation of space networking that differs from terrestrial networks. In a space networking architecture, interplanetary communication protocols need to be designed, validated and evaluated carefully to support different mission requirements."
    },
    {
        "title": "Space Network Time Distribution and Synchronization  Protocol Development  for Mars Proximity Link",
        "authors": [
            "Simon Woo",
            "Jay Gao",
            "David Mills"
        ],
        "venue_full": "AIAA International Conference on Space Operations",
        "venue": "SpaceOps",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2010,
        "links": {
            "conf": "https://doi.org/10.2514/6.2010-2360"
        },
        "img": null,
        "abstract": "Time distribution and synchronization in deep space network are challenging due to long propagation delays, spacecraft movements, and relativistic effects. Further, the Network Time Protocol (NTP) designed for terrestrial networks may not work properly in space"
    },
    {
        "title": "Space Communications and Navigation (SCaN) Network Simulation Tool Development and Its Use Cases",
        "authors": [
            "Esther Jennings",
            "Richard Borgen",
            "Sam Nguyen",
            "John Segui",
            "Tudor Stoenescu",
            "Shin-Ywan Wang",
            "Simon Woo",
            "Brian Barritt",
            "Christine Chevalier",
            "Wesley Eddy"
        ],
        "venue_full": "AIAA Modeling and Simulation Technologies",
        "venue": "MST",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2009,
        "links": {
            "conf": "https://doi.org/10.2514/6.2009-6036"
        },
        "img": null,
        "abstract": "In this work, we focus on the development of a simulation tool to assist in analysis of current and future (proposed) network architectures for NASA. Specifically, the Space Communications and Navigation (SCaN) Network is being architected as an integrated set of new assets\n                                and a federation of upgraded legacy systems. The SCaN architecture for the initial\n                                missions for returning humans to the moon and beyond will include the Space Network (SN)\n                                and the Near-Earth Network (NEN)."
    },
    {
        "title": "Efficient File Sharing by Multicast - P2P Protocol using Network Coding and Rank Based Peer Selection",
        "authors": [
            "Simon S. Woo",
            "Tudor M. Stoenescu"
        ],
        "venue_full": "IEEE Vehicular Technology Conference",
        "venue": "VTC",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2009,
        "links": {
            "conf": "https://doi.org/10.1109/vetecs.2009.5073526"
        },
        "img": null,
        "abstract": "In this work, we consider information dissemination and sharing in a highly dynamic peer-to-peer (P2P) communication network. In particular, we explore a network coding technique for transmission and a rank based peer selection (RBPS) method for network formation."
    },
    {
        "title": "Interfacing Space Network Communications and Navigation Network Simulation with Distributed System Integration Laboratories (DSIL)",
        "authors": [
            "Esther Jennings",
            "Sam Nguyen",
            "Shin-Ywan Wang",
            "Simon Woo"
        ],
        "venue_full": "AIAA International Conference on Space Operations",
        "venue": "SpaceOps",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2008,
        "links": {
            "conf": "https://doi.org/10.2514/6.2008-3462"
        },
        "img": null,
        "abstract": "NASA’s planned Lunar missions will involve multiple NASA centers where each participating center has a specific role and specialization. In this vision, the Constellation program (CxP)’s Distributed System Integration Laboratories (DSIL) architecture consist of multiple System Integration Labs (SILs), with simulators, emulators, testlabs and control centers interacting with each other over a broadband network to perform test and verification for mission scenarios."
    },
    {
        "title": "Prioritized LT codes",
        "authors": [
            "Simon S. Woo",
            "Michael K. Cheng"
        ],
        "venue_full": "IEEE Annual Conference on Information Sciences and Systems",
        "venue": "CISS",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2008,
        "links": {
            "conf": "https://doi.org/10.1109/ciss.2008.4558589"
        },
        "img": null,
        "abstract": "It is common in data transmissions that some information is more important than others. This is especially true in space communications where mission critical information or science data are high priority. In this work, we propose a simple yet constructive scheme to send high priority data reliably and efficiently using Luby transform (LT) codes."
    },
    {
        "title": "A Simulation Tool for ASCTA Microsensor Network Architecture",
        "authors": [
            "Simon Woo",
            "Esther Jennings",
            "Loren Clare"
        ],
        "venue_full": "IEEE Aerospace Conference",
        "venue": " IEEE Aerospace Conf.",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2008,
        "links": {
            "conf": "https://doi.org/10.1109/aero.2008.4526447"
        },
        "img": null,
        "abstract": "Advances in technology have made the large-scale deployment of low-cost networked sensors possible for situational awareness. We developed a Simulation Tool for the Advanced Sensors Collaborative Technology Alliance (ASCTA) Microsensor Network Architecture (STAMINA) to evaluate the performance of networked sensor systems."
    },
    {
        "title": "Improved In Situ Communications Using Network Coding",
        "authors": [
            "Mike Cheng",
            "Simon S. Woo",
            "Kar-Ming Cheung",
            "Sam Dolinar",
            "Jon Hamkins"
        ],
        "venue_full": "Research and Technology Development",
        "venue": "R&TD",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2007,
        "links": {},
        "img": null,
        "abstract": "Advances in technology have made the large-scale deployment of low-cost networked sensors possible for situational awareness. We developed a Simulation Tool for the Advanced Sensors Collaborative Technology Alliance (ASCTA) Microsensor Network Architecture (STAMINA) to evaluate the performance of networked sensor systems."
    },
    {
        "title": "CFDP Performance Over Weather-Dependent Ka-Band Channel",
        "authors": [
            "Simon S. Woo",
            "Jay Gao"
        ],
        "venue_full": "AIAA International Conference on Space Operations",
        "venue": "SpaceOps",
        "track": "Etc.",
        "presentationType": null,
        "Factor": [
            "",
            0
        ],
        "year": 2006,
        "links": {
            "conf": "https://doi.org/10.2514/6.2006-5968"
        },
        "img": null,
        "abstract": "This study presentsan analysis of the delay performance of the CCSDS File Delivery Protocol (CFDP) over weather-dependent Ka-band channel. The Ka-band channel condition is determined by the strength of the atmospheric noise temperature, which is weather dependent."
    }
]
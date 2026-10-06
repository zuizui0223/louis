# King Rails decouple experienced water depth from local hydrological variation

**Manuscript draft V1**

**Authors:** [to be completed]

**Affiliations:** [to be completed]

## Abstract

Animals living in temporally variable landscapes can respond to environmental change not only by abandoning a site, but also by repeatedly using local habitat states that reduce the variation they actually experience. This possibility is central to theories of movement and the experienced environment, yet it is rarely tested against habitat that was locally available at the same observation times. We used an independent public radio-telemetry and microhabitat dataset from western Lake Erie coastal marshes to ask whether resident King Rails (*Rallus elegans*) experienced a more stable hydrological trajectory than nearby time-matched habitat availability.

The source study sampled a used microhabitat plot and nearby random plots during repeated homing events. After source-defined quality control, we reconstructed 190 matched events from 10 birds. For each individual, we generated event-matched pseudo-trajectories by repeatedly drawing from the available random plots. The temporal variance of used water depth was lower than the matched null for all 10 birds: the median State Retention Index was 0.886 (range 0.402–0.976; exact sign-test p = 0.00098). A time-ordered analysis likewise showed smaller successive changes in used water depth than in matched pseudo-trajectories for all birds (median retention 0.658; sign-test p = 0.00098). Hydrological coupling was also strongly reduced: the pooled within-bird slope of used water depth on local available water depth was 0.162, compared with a pseudo-used null median of 1.001, corresponding to an 83.8% reduction in coupling. Restricting comparisons to flooded habitat retained 82–85.5% coupling reduction. Buffering persisted during the most unusual local hydrological conditions for nine of ten individuals, but weakened or failed in some birds.

These results extend static habitat-selection inference by showing that repeated realised microhabitat use can strongly damp temporal environmental variation experienced by resident animals. The public coordinate files cannot yet be joined unambiguously to the matched microhabitat events, so we do not infer that measured geographic displacement caused this buffering. Instead, we identify individual-scale hydrological buffering in realised habitat use and predict that broader relocation should become more likely when suitable local states can no longer be maintained.

**Keywords:** *Rallus elegans*; animal movement; experienced environment; habitat selection; hydrology; microhabitat; niche tracking; wetland ecology

---

## Introduction

Animals experience environments through space use. A local environment can fluctuate strongly through time, yet the environmental sequence actually experienced by an organism need not mirror those local fluctuations if the organism changes where, when, or how it uses habitat. Movement ecology therefore links geographic displacement to environmental regulation: movements alter the resources, risks and physical conditions encountered by an individual, and repeated movement decisions ultimately generate home ranges and habitat-use patterns (Nathan et al. 2008; Van Moorter et al. 2016).

This distinction between the **local environment** and the **experienced environment** has broad theoretical importance. Chesson and Yang (2019) showed that movement across a changing landscape can make the environmental conditions experienced by a population more stationary than conditions at any single locality. Related work on niche construction and habitat choice predicts that organisms can reduce environmental variation by selecting or modifying components of their surroundings (Clark et al. 2020). These theories imply an empirical question that differs from conventional habitat-selection analysis: rather than asking only which habitat states are used more than available, we can ask whether realised space use changes the **temporal variance of the environmental state experienced by an individual**.

Most empirical tests related to environmental tracking operate at broad spatial or seasonal scales. Migrants can follow climatic niches between breeding and non-breeding ranges, and wetland birds may shift among wetlands as inundation changes. At finer scales, however, a resident individual may remain within the same home range while repeatedly using different local patches. Such behaviour could buffer environmental variation without producing obvious broad-scale relocation. This mechanism should be particularly important in wetlands, where shallow topography, water-control structures, precipitation and management can generate strong temporal variation in water depth over short distances.

King Rails (*Rallus elegans*) provide a useful test case. They are wetland specialists whose distribution and behaviour are closely tied to hydrology and vegetative structure. In western Lake Erie coastal marshes, Brewer et al. (2023) radio-tagged King Rails and quantified third-order habitat selection within breeding-season home ranges. For 10 birds whose home ranges stabilized, mean home-range size was 8.8 ha, and used microhabitats were associated with dense vegetation and shallow water. The source study reported that approximately 75% of King Rail locations occurred at water depths of roughly 6–17 cm and recommended maintaining a diversity of shallow-water conditions for management.

Those results establish a hydrological niche but do not ask whether birds **stabilize the water-depth trajectory they experience through time**. A habitat-selection contrast can show that used locations differ from random locations on average while leaving open whether temporal changes in local availability are transmitted directly into the conditions used by each individual. For example, if all locally available patches become deeper through time and birds simply continue using the same patch, used water depth should track available water depth strongly. Conversely, if birds repeatedly use alternative local patches as hydrology changes, used water depth may remain relatively stable even while nearby availability fluctuates.

The Lake Erie dataset contains an unusually direct counterfactual for this temporal question. At repeated homing events, the source study measured microhabitat at the bird's used location and at nearby random plots sampled within the same short time window. Thus, for each bird and event, the data contain both the hydrological state experienced by the bird and a local availability set exposed to approximately the same broad environmental conditions.

We used this matched design to test three nested predictions. First, we predicted that the temporal variance of used water depth would be smaller than the variance of pseudo-trajectories assembled from event-matched random points. Second, because a low overall variance could arise without temporal continuity, we predicted that successive changes in used water depth would also be smaller than successive changes in matched pseudo-trajectories. Third, we asked how strongly changes in nearby available water depth were transmitted into used water depth. If realised habitat use buffers hydrological variation, the within-individual slope of used water depth on local available water depth should be substantially shallower than a pseudo-used null generated from the same matched availability sets.

We further evaluated two limits of interpretation. We repeated the analysis after excluding dry availability points to determine whether the result was merely wet-versus-dry selection. We also examined events in which local available water depth was unusually different from each bird's typical hydrological context to ask whether buffering persisted under stronger local mismatch. Finally, because the archived coordinate files cannot be unambiguously linked to the matched microhabitat-event IDs, we deliberately distinguish **hydrological buffering by realised habitat use** from the stronger, currently unsupported claim that measured geographic displacement caused that buffering.

---

## Methods

### Study system and source data

We analysed publicly archived data from Brewer et al. (2023), who studied King Rail home range and microhabitat characteristics in western Lake Erie coastal marshes during 2019–2021. The source study radio-tagged 14 King Rails in northwestern Ohio and southeastern Michigan. Ten individuals developed stable breeding-season home ranges and were included in the source study's home-range and third-order microhabitat analyses.

The source study recorded microhabitat at repeated King Rail homing locations and paired those measurements with local random plots. Random plots were placed approximately 75 m from the used location in random directions and were surveyed within 72 h of the homing event. Water depth was calculated as the mean of five measurements at each plot. The public data and code are archived at Zenodo (DOI: 10.5281/zenodo.6604660).

Our analyses were not part of the original habitat-selection study. We used the published data structure to test a new temporal, availability-relative hypothesis developed independently of the Lake Erie outcome sequence. We therefore treat the present analysis as an independent-data developmental test rather than a preregistered analysis.

### Reconstruction of matched events

We used the archived table `CARTdataset_12.31.21_All_D.csv`. The source table contained 607 rows.

We followed source-defined quality-control semantics. Rows with `Missing = Yes` were excluded. Point identifiers encode individual identity, point type and repeated homing-event number. For example:

~~~text
165.020H1_21
165.020R1_1_21
165.020R1_2_21
~~~

represent the used point and two random points for the same event of bird `020_21`.

We parsed identifiers under one fixed regular expression. Two malformed source IDs failed that parser and were excluded without repair. We did not infer their intended event identities manually.

After excluding 17 source-defined missing rows and two malformed IDs, we reconstructed 190 valid matched events across 10 birds. A valid event required exactly one used point and at least one random point with a unique year and Julian date. Of these, 173 events retained both intended random plots.

The individual bird was the biological replication unit. Point rows and repeated events were treated as repeated observations within individuals rather than independent biological replicates.

### State Retention Index

For individual (i), let (U_{it}) denote used water depth at event (t). At the same event, let (R_{it}) be the set of one or more retained random-plot water depths.

We first quantified whether the temporal distribution of used water depths was narrower than expected from local availability. The observed statistic was:

\[
V_{i,\mathrm{used}} = \operatorname{Var}_t(U_{it}).
\]

For each Monte Carlo pseudo-trajectory, one random depth was selected from (R_{it}) at every real event, preserving the actual temporal sequence and local availability structure. We repeated this procedure 100,000 times per individual.

We defined the State Retention Index:

\[
\mathrm{SRI}_i
=
1 -
\frac{V_{i,\mathrm{used}}}
{\operatorname{median}_b(V_{i,\mathrm{null}}^{(b)})}.
\]

Positive SRI means that the water-depth states used by a bird varied less through time than event-matched local availability. SRI of zero indicates equal temporal variance, and negative values indicate greater variation in used than pseudo-used states.

We used deterministic xorshift32 pseudorandom generation with a fixed seed family derived from base seed 20261001 and individual identity. Individual lower-tail Monte Carlo probabilities used an add-one correction. At the population level, we tested directional consistency with an exact one-sided sign test on the number of birds with positive SRI.

As a strict availability sensitivity, we repeated the analysis using only events in which both random plots survived source-defined quality control.

### Time-ordered state retention

Variance ignores event order. A trajectory that alternates between two extreme states can have the same variance as one that changes slowly.

We therefore repeated the matched-pseudo-trajectory analysis using mean absolute successive change:

\[
\Delta_{i,\mathrm{used}}
=
\frac{1}{T_i-1}
\sum_{t=2}^{T_i}
|U_{it}-U_{i,t-1}|.
\]

Events were ordered within individual by year, Julian date and event number. For every null trajectory, we calculated the same statistic after drawing one event-matched random plot at each observation.

Temporal retention was defined analogously to SRI:

\[
\mathrm{TR}_i
=
1 -
\frac{\Delta_{i,\mathrm{used}}}
{\operatorname{median}_b(\Delta_{i,\mathrm{null}}^{(b)})}.
\]

Positive values indicate smaller successive changes in used water depth than expected from matched availability.

### Flooded-habitat sensitivities

A trivial explanation for state retention would be that random plots sometimes represented dry ground whereas birds preferentially used flooded habitat. We therefore ran two post-hoc robustness analyses.

In the **conditional-flooded** analysis, random plots with water depth \(\le 0\) were removed before generating pseudo-trajectories. Events were retained if at least one flooded random point remained.

In the **all-points-flooded** analysis, an event was retained only if the used point and all retained random points had water depth \(>0\).

For each filtered dataset, we recalculated variance retention and time-ordered retention under the same individual-level matched-pseudo-trajectory logic.

### Hydrological availability coupling

SRI asks whether used states vary less than available states. We next asked how strongly temporal changes in local availability were transmitted into the state used by the bird.

For event (t), we defined:

\[
A_{it} = \operatorname{mean}(R_{it}),
\]

and retained (U_{it}) as the observed used water depth.

Within birds, we estimated the slope relating (U_{it}) to (A_{it}). We pooled the within-bird centred covariance and variance across individuals to obtain a common descriptive slope while preserving individual centring.

For the null, one matched random point was selected as pseudo-used at every event and the identical within-bird slope was recomputed. We used 20,000 individual and pooled pseudo-used replicates with base seed 20261003.

A pseudo-used trajectory sampled from the same local availability set should, by construction, couple strongly to mean local availability. Thus, an observed slope much shallower than the pseudo-used distribution indicates that variation in local available water depth is only weakly expressed in the used hydrological state.

We expressed the magnitude descriptively as:

\[
1 -
\frac{\beta_{\mathrm{used}}}
{\operatorname{median}(\beta_{\mathrm{null}})}.
\]

We repeated this analysis under the flooded-random and all-points-flooded filters.

### Buffering-limit decomposition

After establishing the primary independent state-retention result, we conducted a post-hoc mechanism decomposition to ask whether buffering persisted during unusually mismatched local hydrological conditions.

For each bird, we calculated its median available depth and defined event-level availability mismatch:

\[
X_{it}
=
|A_{it} - \operatorname{median}_t(A_{it})|.
\]

We similarly defined experienced-state deviation:

\[
Y_{it}
=
|U_{it} - \operatorname{median}_t(U_{it})|.
\]

We estimated the within-bird pooled slope of (Y) on (X), and compared it with a pseudo-used null generated from event-matched random plots.

For an extreme-condition sensitivity, we defined extreme events as the top quartile of (X) within each bird. This rule was based only on each bird's availability distribution and did not use used-water-depth outcomes to choose a biological threshold. We compared mean experienced-state deviation during those events with the same statistic under 50,000 matched pseudo-used trajectories.

This analysis was explicitly post-hoc and was not treated as a second independent validation.

### Local hydrological heterogeneity mechanism decomposition

We next asked whether fine-scale heterogeneity in local water depth provided a measurable opportunity for buffering. This analysis was also post-hoc and used only the 173 matched events for which both intended random plots survived source-defined quality control.

For each event, we defined local mean availability as the mean of the two random-plot water depths and local hydrological heterogeneity as their range:

\[
H_{it}=\max(R_{it})-\min(R_{it}).
\]

As in the buffering-limit analysis, local mean-state mismatch was:

\[
X_{it}=|A_{it}-\operatorname{median}_t(A_{it})|,
\]

and experienced-state deviation was:

\[
Y_{it}=|U_{it}-\operatorname{median}_t(U_{it})|.
\]

We fit a pooled within-bird regression of \(Y\) on \(X\) and \(H\). The focal quantity was the heterogeneity coefficient after bird-level centring.

To construct a matched null, we selected one of the two real random plots as pseudo-used at every event, recomputed each bird's pseudo-used median and refit the identical model. We repeated this procedure 50,000 times. This preserves the observed local mismatch and heterogeneity sequence while removing the realised used-state choice.

A secondary model added an \(X\times H\) interaction to test whether heterogeneity became disproportionately more useful during unusually mismatched hydrological conditions. Neither analysis identifies geographic movement because the event-level coordinate join remains unresolved.

### Coordinate-linkage audit

The public archive also contains individual UTM coordinate files used for home-range estimation. Those files do not include an explicit event/date key matching rows to the homing-event identifiers in the microhabitat table.

We audited possible row-order matching and found a mixture of clean and irregular cases, including skipped or malformed event numbers. Because row-order equivalence is not independently documented, we did not join coordinate rows to microhabitat events.

Consequently, our primary inference concerns the temporal environmental states represented by realised microhabitat use. We do not estimate the geographic displacement required to produce that state retention.

---

## Results

### Matched-event reconstruction

The archived microhabitat table contained 607 rows. Seventeen rows marked `Missing = Yes` were excluded under the source study's rule. Two additional rows contained malformed point identifiers and were excluded without repair.

The resulting dataset contained 190 valid matched used/random events from 10 individual King Rails. Both random points were retained in 173 events.

### Used water-depth trajectories were more stable than matched availability

All ten birds had positive State Retention Indices.

Median SRI was **0.886**, mean SRI was **0.764**, and individual values ranged from **0.402 to 0.976**. The exact probability of observing 10 positive values in 10 birds under a symmetric sign null was **p = 0.00098**.

Nine of ten individuals had lower-tail Monte Carlo probabilities below 0.05. Thus, the directional population-level result was not generated by a small subset of birds.

Restricting the analysis to the 173 events for which both random plots were retained produced almost identical results: all ten birds remained positive, median SRI was **0.882**, and the range was **0.369–0.976**.

### Temporal continuity was also stronger than matched availability

The difference was not limited to overall variance. When event order was retained, all ten birds showed smaller successive changes in used water depth than in their event-matched pseudo-trajectories.

Median temporal retention was **0.658**, with individual values from **0.388 to 0.879**. The sign test was again **p = 0.00098**, and all ten individuals had Monte Carlo probabilities below 0.05.

Under the strict two-random-point subset, all ten birds again remained positive and median temporal retention was **0.667**.

Thus, used hydrological states were both narrower in distribution and smoother through time than local availability.

### State retention persisted within flooded habitat

Conditioning random availability on flooded points left 182 events. All ten birds retained positive temporal state retention, with median retention **0.622** and sign-test **p = 0.00098**. All ten individual temporal randomization tests remained below 0.05.

Requiring the used point and all retained random points to be flooded left 131 events. Again, all ten birds were positive, with median temporal retention **0.528** and sign-test **p = 0.00098**.

The primary result therefore could not be reduced to birds simply selecting flooded locations while random points sometimes fell on dry ground.

### Only a small fraction of local hydrological variation was transmitted into used state

Across the 190 primary events, the pooled within-bird slope of used water depth on mean local available depth was **0.162**.

Matched pseudo-used trajectories had a median slope of **1.001**. Relative to that null, the observed coupling was reduced by **83.8%** (Monte Carlo lower-tail p < **5 (	imes) 10(^{-5})**).

At the individual level, the median observed slope was **0.122** and the median coupling reduction was **87.8%**. All ten birds had observed slopes below their own pseudo-used null medians, and all ten had individual Monte Carlo p < 0.05.

Flooded-habitat restrictions produced the same result. When dry random plots were removed, the observed slope was **0.145** versus a null median of approximately 1.000, a coupling reduction of **85.5%**. When all retained used and random points were required to be flooded, the observed slope was **0.180**, corresponding to **82.0%** coupling reduction.

Thus, temporal variation in nearby available water depth was only weakly expressed in the water depth used by the birds.

### Buffering persisted under strong mismatch but showed individual limits

When local hydrological mismatch was defined as the absolute deviation of available depth from each bird's median available state, the pooled slope relating experienced-state deviation to availability mismatch was **0.115**, versus a pseudo-used null median of **0.741**. This corresponded to **84.5%** coupling reduction (Monte Carlo p < **2 (	imes) 10(^{-5})**).

All ten individuals had mismatch slopes below their pseudo-used null medians.

During the top quartile of local mismatch events within each bird, nine of ten individuals retained positive environmental-state buffering. Median extreme-condition retention was **0.629**, and seven of ten individuals had lower-tail Monte Carlo p < 0.05.

One individual showed slightly negative extreme retention and several showed substantially weaker buffering than the strongest individuals. Thus, hydrological buffering was widespread but not unlimited.

### Local hydrological heterogeneity was associated with buffering opportunity

Among the 173 events with two retained random plots, the within-bird coefficient relating local random-depth range to experienced-state deviation, after representing mean-state mismatch, was **-0.0431**. Under 50,000 matched pseudo-used trajectories generated from the same local random plots, the median heterogeneity coefficient was **+0.2617**. The observed value lay in the extreme lower tail of the matched null (**p = 0.000020**).

Thus, broader simultaneous local water-depth availability was associated with less displacement of the state actually used than expected if used states were drawn from the same local availability set.

The stronger mismatch-by-heterogeneity prediction was not supported. Its observed interaction coefficient was **-0.00490**, compared with a matched-null median of **-0.00940** (**p = 0.753**). We therefore do not infer that heterogeneity becomes disproportionately more protective under extreme hydrological mismatch.

---

## Discussion

### Resident King Rails experience a buffered hydrological environment

The central result is simple: the hydrological conditions used by individual King Rails changed much less through time than the hydrological conditions that were locally available at the same observation events.

This pattern appeared in three complementary statistics. First, temporal variance in used water depth was lower than matched availability for every bird. Second, successive changes in used water depth were smaller than matched pseudo-trajectories for every bird. Third, the direct coupling of used depth to local available depth was shallow: a pooled slope of 0.162 compared with a pseudo-used expectation near one.

Together, these results support a view of realised microhabitat use as a form of **environmental buffering**. The birds occupied a dynamic marsh but did not experience the full temporal hydrological variation occurring nearby.

This is more specific than ordinary habitat preference. Brewer et al. (2023) showed that King Rails frequently used shallow water and particular vegetation structures. A stable preference for shallow water could produce lower mean used depth than random locations. It does not automatically imply that an individual's used trajectory will remain temporally stable as local availability changes. The matched temporal analysis shows that this additional property is present.

### An individual-scale empirical example of the experienced-environment problem

The distinction between local and experienced environments has a clear theoretical precedent.

Chesson and Yang (2019) showed that a population moving across a heterogeneous changing landscape can experience environmental conditions that are more stationary than those at any single location. Their framework emphasizes that environmental change and redistribution can partly offset one another.

Clark et al. (2020) approached a related problem through niche construction and environmental regulation, arguing that organism-chosen or organism-modified environmental sources can buffer environmental variability. Habitat choice is one of the mechanisms through which organisms alter the conditions they experience.

Our result is narrower and empirical. We do not estimate a population-level moving environmental distribution or long-term climate tracking. Instead, we use repeated matched availability to quantify, within individual resident birds, how much local temporal hydrological variation appears in the environmental state actually used.

That scale distinction matters. King Rails in the Lake Erie study occupied relatively small breeding home ranges. Environmental buffering therefore does not require continental migration or even seasonal range change. It can emerge from repeated fine-scale habitat use inside a familiar marsh.

### Movement and habitat selection are linked, but geographic mechanism remains unresolved here

Movement theory emphasizes that geographic relocation is the process connecting habitat selection and home-range structure (Van Moorter et al. 2016). In that sense, repeated used microhabitats must ultimately arise from movement or continued residence.

However, the current archive does not permit a clean event-level estimate of geographic displacement between the exact microhabitat observations used here. The separate UTM coordinate files lack event/date keys, and source irregularities make row-order joining unsafe.

We therefore stop one step short of saying that measured displacement generated the buffering.

This distinction is scientifically useful rather than merely technical. Our direct result is about **experienced environmental state**. Whether birds achieved it by frequent short movements, longer relocations among internal patches, differential residence time, repeated return to particular patches, or some combination remains open.

An original dated event-keyed telemetry table would allow a stronger analysis of the trade-off between distance moved in geographic space and distance moved in environmental-state space.

### The result is not a wet-versus-dry artifact

Because King Rails are marsh birds, one trivial explanation is that random points include dry habitat and used locations simply remain wet.

The flooded-only analyses reject that explanation as sufficient. Strong state retention remained after excluding dry random points, and it remained when every retained used and random point was flooded. Hydrological coupling reduction also remained between approximately 82% and 86%.

Thus, the relevant signal is quantitative within wet habitat. Birds repeatedly used particular water-depth states rather than merely selecting the binary presence of water.

This distinction matters for management. Maintaining wetland area or inundation alone may not retain the environmental states used by a hydrological specialist. The distribution of shallow-water conditions through space and time can be equally important.

### Local heterogeneity provides a candidate state portfolio

The post-hoc heterogeneity analysis adds a mechanism-level clue to the primary buffering result. When two nearby random plots spanned a wider range of water depths, the water depth actually used by the bird was less displaced from its typical state than expected from matched pseudo-use, after the shift in mean local availability was represented.

This pattern is consistent with a **local state portfolio** interpretation. Fine-scale environmental heterogeneity can provide simultaneous alternatives rather than merely increasing habitat variance. If an animal can select among those alternatives, geographic space may contain a broader range of states while the environmental state actually experienced remains comparatively narrow.

The comparison with matched pseudo-use is important. Broader random-plot depth ranges by themselves tended to generate greater pseudo-used state displacement; the realised used-state relationship differed strongly from that expectation. The result therefore goes beyond the statement that heterogeneous wetlands contain more variable habitat.

However, two random plots provide only a sparse sample of the local hydrological distribution, and the analysis was developed after the primary buffering result. It does not establish how much heterogeneity is required, whether the birds physically visited the sampled alternatives, or whether heterogeneity prevents emigration. A complete dynamic habitat surface linked to event-level movement would be needed to identify failure of the local state portfolio directly.

### Buffering is strong but finite

The buffering-limit analysis provides an important counterpoint to the strong primary result.

Nine of ten individuals still retained positive buffering during their most unusual local hydrological conditions, but one did not, and several showed weaker effects. We therefore do not interpret environmental-state retention as perfect homeostasis.

Instead, the data suggest a **capacity for local compensation**. When hydrological states change, birds can often continue using conditions closer to their typical used state than a random local trajectory would provide. The capacity varies among individuals and may fail when suitable internal alternatives become scarce, inaccessible, or otherwise unsuitable.

This interpretation connects naturally to recent telemetry from a resident King Rail population in the South Carolina Lowcountry. Linke and McRae (2026) found that five of nine birds with both breeding and non-breeding telemetry shifted seasonal home ranges, with a mean shift of 2.9 km and a range of 0.7–7.5 km. Birds moved into adjacent tidal marsh or flooded forest when managed impoundments were flooded for waterfowl or otherwise altered. That study does not reproduce our event-matched buffering metric, but it illustrates the broader relocation regime expected when local habitat-state compensation becomes insufficient.

The combined ecological prediction is therefore continuous rather than categorical: local hydrological heterogeneity may allow fine-scale environmental buffering, whereas loss of suitable states within the familiar area should increase the spatial scale required to restore acceptable conditions.

### Management should consider hydrological portfolios, not only average depth

The source study recommended maintaining water depths of approximately 6–17 cm and a diversity of dense emergent vegetation for King Rails. Our results add a temporal interpretation to that recommendation.

A marsh with the correct **mean** water depth can still be poor habitat if all patches change in the same direction at the same time. Conversely, a spatially heterogeneous marsh may retain suitable shallow states somewhere within a bird's familiar area as water levels fluctuate.

We did not reconstruct a complete dynamic water-depth surface, so we have not directly estimated the fraction of each home range that remained suitable at each time. A full hydrological-portfolio analysis remains a future extension.

Nevertheless, the observed buffering relative to nearby availability implies that management should be cautious about homogenizing water depth. Maintaining internal elevation, depth and vegetation heterogeneity may provide alternative local states that resident birds can use under changing hydrological conditions.

This is particularly relevant in impounded coastal wetlands, where water levels are often actively manipulated. Management that simultaneously eliminates shallow-water refugia across an entire impoundment may impose a qualitatively different constraint from management that alters average water level while retaining a mosaic of suitable states.

### Limitations and evidence boundaries

Our study has several important limitations.

First, the biological replication level is ten birds. The result is unusually consistent across those birds, but the sample represents one regional population and one managed wetland system. Generalization to other King Rail populations or wetland birds requires independent replication of the same availability-relative temporal estimand.

Second, the analysis uses water depth as a focal environmental axis. King Rails respond to vegetation density, plant composition, cover, open-water proximity, prey and predation risk as well as hydrology. A bird may accept greater variation in one environmental dimension to stabilize another. Multivariate experienced-environment analyses would be valuable but should be designed prospectively rather than selected after viewing the present result.

Third, the random points represent local availability under the source study's sampling design. Our inference is therefore about buffering relative to that local choice set, not all habitat potentially reachable by a bird.

Fourth, the coordinate-to-event linkage is unresolved, preventing a direct test of how geographic movement distance produces hydrological state retention.

Fifth, the buffering-limit analysis was developed after the primary state-retention result and is post-hoc. It is useful for mechanism development but should not be described as an independently validated threshold.

Finally, the analysis was generated from a hypothesis developed after a separate ecological analysis and applied to an independent public dataset. It is independent-data evidence, but it was not preregistered.

### Conclusion

Resident King Rails in western Lake Erie coastal marshes repeatedly used microhabitats whose water depths were far more temporally stable than the water depths locally available at the same observation times. Local hydrological variation was strongly damped in realised use, and the effect remained quantitative within flooded habitat.

These results provide an individual-scale empirical demonstration that an animal's experienced environment can be more stable than its local environment even without broad-scale migration. Buffering was strong but finite, suggesting a transition from local compensation to broader relocation when suitable internal habitat states can no longer be retained.

The ecological implication is that residency and environmental stability are not synonymous with immobility or with a static landscape. A dynamic wetland can support resident animals when its spatial structure continues to provide accessible alternatives that keep experienced conditions within a comparatively narrow range.

---

## Data and code availability

The source King Rail data and code are publicly archived by Brewer et al. (2023) at Zenodo, DOI **10.5281/zenodo.6604660**.

The present analysis code, contracts and derived canonical summaries are maintained in this repository. The primary manuscript values are frozen in:

- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V2.json`.

Key analysis scripts:

- `analysis/08_lake_erie_standardize.py`
- `analysis/09_lake_erie_state_fidelity.py`
- `analysis/11_lake_erie_flooded_availability_sensitivity.py`
- `analysis/12_lake_erie_availability_coupling.py`
- `analysis/13_lake_erie_buffering_limits.py`
- `analysis/15_lake_erie_local_heterogeneity_insurance.py`

The coordinate-to-event linkage is intentionally not reconstructed by undocumented row order.

---

## References — core set for manuscript development

Brewer, R. et al. (2023). King rail (*Rallus elegans*) home range and microhabitat characteristics in western Lake Erie coastal marshes. *Ecology and Evolution* 13: e10043. https://doi.org/10.1002/ece3.10043

Chesson, P. & Yang, P.J. (2019). Populations as fluid on a landscape under global environmental change. *Frontiers in Ecology and Evolution* 7:363. https://doi.org/10.3389/fevo.2019.00363

Clark, A.D., Deffner, D., Laland, K., Odling-Smee, J. & Endler, J. (2020). Niche construction affects the variability and strength of natural selection. *The American Naturalist* 195:16–30. https://doi.org/10.1086/706196

Linke, M.M. & McRae, S.B. (2026). Seasonal movements and habitat use of a threatened rail among fragmented riparian tidal wetlands and impoundments: management implications. *Frontiers in Conservation Science* 7. https://doi.org/10.3389/fcosc.2026.1894344

Nathan, R. et al. (2008). A movement ecology paradigm for unifying organismal movement research. *Proceedings of the National Academy of Sciences USA* 105:19052–19059.

Van Moorter, B. et al. (2016). Movement is the glue connecting home ranges and habitat selection. *Journal of Animal Ecology* 85. https://doi.org/10.1111/1365-2656.12394

[Additional King Rail and wetland-hydrology references to be completed during journal formatting.]
